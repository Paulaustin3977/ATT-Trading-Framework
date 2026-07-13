//+------------------------------------------------------------------+
//| Austin_M15_Scalper_v1.0.mq5                                     |
//| Milestone 1 + completed-candle pullback strategy                 |
//| Research build: no martingale, no grid, one position at a time   |
//+------------------------------------------------------------------+
#property copyright "Austin Trading Team"
#property version   "1.00"
#property strict

#include <Trade/Trade.mqh>

CTrade trade;

//--------------------------------------------------------------------
// Inputs
//--------------------------------------------------------------------
input group "General Settings"
input ulong           InpMagicNumber             = 15091501;
input ENUM_TIMEFRAMES InpEntryTimeframe          = PERIOD_M15;
input ENUM_TIMEFRAMES InpTrendTimeframe          = PERIOD_H1;
input bool            InpAllowLongs              = true;
input bool            InpAllowShorts             = true;
input bool            InpOnePositionOnly         = true;
input int             InpSlippagePoints          = 30;
input bool            InpVerboseLogging          = true;

input group "M15 Pullback Signal"
input int             InpFastEMA                 = 9;
input int             InpMediumEMA               = 21;
input int             InpTrendEMA                = 50;
input int             InpEMASlopeLookback        = 3;
input double          InpPullbackATRBuffer        = 0.15;
input bool            InpRequireCandleDirection  = true;

input group "H1 Trend Filter"
input int             InpHTFFastEMA              = 50;
input int             InpHTFSlowEMA              = 200;
input int             InpHTFSlopeLookback        = 3;

input group "Momentum Filter"
input int             InpADXPeriod               = 14;
input double          InpMinimumADX              = 20.0;
input double          InpMaximumADX              = 55.0;

input group "Volatility and Stops"
input int             InpATRPeriod               = 14;
input double          InpStopATRMultiplier       = 1.50;
input double          InpTargetRMultiple         = 1.50;
input double          InpMinimumATRPoints        = 0.0;
input double          InpMaximumATRPoints        = 0.0;
input int             InpMinimumStopPoints       = 0;
input int             InpMaximumStopPoints       = 0;

input group "Risk Management"
input bool            InpRiskFromEquity          = true;
input double          InpRiskPercent             = 0.25;
input double          InpMaximumRiskPercent      = 2.00;
input int             InpMaximumDailyTrades      = 6;
input double          InpMaximumDailyLossPercent = 2.00;
input int             InpMaximumConsecutiveLosses= 3;
input int             InpCooldownBarsAfterLoss   = 2;

input group "Session Filter - Broker Time"
input bool            InpUseSessionFilter        = true;
input int             InpSessionStartHour        = 7;
input int             InpSessionStartMinute      = 0;
input int             InpSessionEndHour          = 20;
input int             InpSessionEndMinute        = 0;
input bool            InpTradeMonday             = true;
input bool            InpTradeTuesday            = true;
input bool            InpTradeWednesday          = true;
input bool            InpTradeThursday           = true;
input bool            InpTradeFriday             = true;

input group "Spread Protection"
input int             InpMaximumSpreadPoints     = 80;
input double          InpMaximumSpreadATRPercent = 12.0;

//--------------------------------------------------------------------
// Indicator handles
//--------------------------------------------------------------------
int hM15FastEMA   = INVALID_HANDLE;
int hM15MediumEMA = INVALID_HANDLE;
int hM15TrendEMA  = INVALID_HANDLE;
int hH1FastEMA    = INVALID_HANDLE;
int hH1SlowEMA    = INVALID_HANDLE;
int hADX          = INVALID_HANDLE;
int hATR          = INVALID_HANDLE;

datetime g_lastBarTime       = 0;
datetime g_lastEntryBarTime  = 0;
bool     g_orderInProgress   = false;

//--------------------------------------------------------------------
// Utility logging
//--------------------------------------------------------------------
void Log(const string message)
{
   if(InpVerboseLogging)
      Print("[Austin M15 Scalper] ", message);
}

void Reject(const string reason)
{
   Log("ENTRY REJECTED: " + reason);
}

//--------------------------------------------------------------------
// Date and history helpers
//--------------------------------------------------------------------
datetime StartOfBrokerDay()
{
   MqlDateTime dt;
   TimeToStruct(TimeCurrent(), dt);
   dt.hour = 0;
   dt.min  = 0;
   dt.sec  = 0;
   return StructToTime(dt);
}

bool IsOurDeal(const ulong ticket)
{
   if(ticket == 0)
      return false;

   if((ulong)HistoryDealGetInteger(ticket, DEAL_MAGIC) != InpMagicNumber)
      return false;

   if(HistoryDealGetString(ticket, DEAL_SYMBOL) != _Symbol)
      return false;

   return true;
}

double GetTodayClosedProfit()
{
   datetime from = StartOfBrokerDay();
   datetime to   = TimeCurrent();

   if(!HistorySelect(from, to))
      return 0.0;

   double pnl = 0.0;
   int total = HistoryDealsTotal();

   for(int i = 0; i < total; i++)
   {
      ulong ticket = HistoryDealGetTicket(i);
      if(!IsOurDeal(ticket))
         continue;

      ENUM_DEAL_ENTRY entry =
         (ENUM_DEAL_ENTRY)HistoryDealGetInteger(ticket, DEAL_ENTRY);

      if(entry != DEAL_ENTRY_OUT && entry != DEAL_ENTRY_OUT_BY)
         continue;

      pnl += HistoryDealGetDouble(ticket, DEAL_PROFIT);
      pnl += HistoryDealGetDouble(ticket, DEAL_SWAP);
      pnl += HistoryDealGetDouble(ticket, DEAL_COMMISSION);
   }
   return pnl;
}

int GetTodayEntryCount()
{
   datetime from = StartOfBrokerDay();
   datetime to   = TimeCurrent();

   if(!HistorySelect(from, to))
      return 0;

   int count = 0;
   int total = HistoryDealsTotal();

   for(int i = 0; i < total; i++)
   {
      ulong ticket = HistoryDealGetTicket(i);
      if(!IsOurDeal(ticket))
         continue;

      ENUM_DEAL_ENTRY entry =
         (ENUM_DEAL_ENTRY)HistoryDealGetInteger(ticket, DEAL_ENTRY);

      if(entry == DEAL_ENTRY_IN || entry == DEAL_ENTRY_INOUT)
         count++;
   }
   return count;
}

int GetConsecutiveLosses(datetime &lastLossTime)
{
   lastLossTime = 0;

   if(!HistorySelect(0, TimeCurrent()))
      return 0;

   int losses = 0;

   for(int i = HistoryDealsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = HistoryDealGetTicket(i);
      if(!IsOurDeal(ticket))
         continue;

      ENUM_DEAL_ENTRY entry =
         (ENUM_DEAL_ENTRY)HistoryDealGetInteger(ticket, DEAL_ENTRY);

      if(entry != DEAL_ENTRY_OUT && entry != DEAL_ENTRY_OUT_BY)
         continue;

      double result = HistoryDealGetDouble(ticket, DEAL_PROFIT)
                    + HistoryDealGetDouble(ticket, DEAL_SWAP)
                    + HistoryDealGetDouble(ticket, DEAL_COMMISSION);

      datetime dealTime =
         (datetime)HistoryDealGetInteger(ticket, DEAL_TIME);

      if(result < 0.0)
      {
         if(lastLossTime == 0)
            lastLossTime = dealTime;
         losses++;
      }
      else
      {
         break;
      }
   }
   return losses;
}

//--------------------------------------------------------------------
// Position and market checks
//--------------------------------------------------------------------
bool HasOurOpenPosition()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0)
         continue;

      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;

      if((ulong)PositionGetInteger(POSITION_MAGIC) != InpMagicNumber)
         continue;

      return true;
   }
   return false;
}

bool IsTradingDayAllowed()
{
   MqlDateTime dt;
   TimeToStruct(TimeCurrent(), dt);

   switch(dt.day_of_week)
   {
      case 1: return InpTradeMonday;
      case 2: return InpTradeTuesday;
      case 3: return InpTradeWednesday;
      case 4: return InpTradeThursday;
      case 5: return InpTradeFriday;
   }
   return false;
}

bool IsInsideSession()
{
   if(!InpUseSessionFilter)
      return true;

   if(!IsTradingDayAllowed())
      return false;

   MqlDateTime dt;
   TimeToStruct(TimeCurrent(), dt);

   int nowMinutes   = dt.hour * 60 + dt.min;
   int startMinutes = InpSessionStartHour * 60 + InpSessionStartMinute;
   int endMinutes   = InpSessionEndHour * 60 + InpSessionEndMinute;

   if(startMinutes == endMinutes)
      return true;

   if(startMinutes < endMinutes)
      return (nowMinutes >= startMinutes && nowMinutes < endMinutes);

   // Session crosses midnight.
   return (nowMinutes >= startMinutes || nowMinutes < endMinutes);
}

bool IsNewEntryBar()
{
   datetime currentBar = iTime(_Symbol, InpEntryTimeframe, 0);
   if(currentBar <= 0)
      return false;

   if(currentBar == g_lastBarTime)
      return false;

   g_lastBarTime = currentBar;
   return true;
}

bool MarketAndSymbolAreValid()
{
   if(!SymbolSelect(_Symbol, true))
   {
      Log("SymbolSelect failed for " + _Symbol);
      return false;
   }

   long tradeMode = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_MODE);
   if(tradeMode == SYMBOL_TRADE_MODE_DISABLED)
   {
      Log("Trading is disabled for " + _Symbol);
      return false;
   }

   double tickSize  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double volMin    = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double volStep   = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);

   if(tickSize <= 0.0 || tickValue <= 0.0 || volMin <= 0.0 || volStep <= 0.0)
   {
      Log("Invalid symbol properties: tick size/value or volume limits.");
      return false;
   }
   return true;
}

//--------------------------------------------------------------------
// Buffer and price helpers
//--------------------------------------------------------------------
bool CopyIndicatorValues(const int handle,
                         const int buffer,
                         const int start,
                         const int count,
                         double &values[])
{
   ArrayResize(values, count);
   ArraySetAsSeries(values, true);

   ResetLastError();
   int copied = CopyBuffer(handle, buffer, start, count, values);
   if(copied != count)
   {
      Log(StringFormat("CopyBuffer failed. handle=%d buffer=%d copied=%d error=%d",
                       handle, buffer, copied, GetLastError()));
      return false;
   }
   return true;
}

bool GetRates(const ENUM_TIMEFRAMES timeframe,
              const int start,
              const int count,
              MqlRates &rates[])
{
   ArrayResize(rates, count);
   ArraySetAsSeries(rates, true);

   ResetLastError();
   int copied = CopyRates(_Symbol, timeframe, start, count, rates);
   if(copied != count)
   {
      Log(StringFormat("CopyRates failed. timeframe=%d copied=%d error=%d",
                       timeframe, copied, GetLastError()));
      return false;
   }
   return true;
}

//--------------------------------------------------------------------
// Risk and volume calculations
//--------------------------------------------------------------------
int VolumeDigits()
{
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   int digits = 0;

   while(digits < 8 && NormalizeDouble(step, digits) != step)
      digits++;

   return digits;
}

double NormalizeVolumeDown(double volume)
{
   double minimum = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maximum = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double step    = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);

   if(step <= 0.0)
      return 0.0;

   volume = MathMin(volume, maximum);
   volume = MathFloor((volume + 1e-12) / step) * step;
   volume = NormalizeDouble(volume, VolumeDigits());

   if(volume < minimum)
      return 0.0;

   return volume;
}

double CalculateRiskVolume(const double entryPrice, const double stopPrice)
{
   double riskPercent = MathMin(InpRiskPercent, InpMaximumRiskPercent);
   if(riskPercent <= 0.0)
      return 0.0;

   double capital = InpRiskFromEquity
                  ? AccountInfoDouble(ACCOUNT_EQUITY)
                  : AccountInfoDouble(ACCOUNT_BALANCE);

   double riskMoney = capital * riskPercent / 100.0;
   double distance  = MathAbs(entryPrice - stopPrice);

   double tickSize  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE_LOSS);

   if(tickValue <= 0.0)
      tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);

   if(riskMoney <= 0.0 || distance <= 0.0 ||
      tickSize <= 0.0 || tickValue <= 0.0)
      return 0.0;

   double lossPerLot = (distance / tickSize) * tickValue;
   if(lossPerLot <= 0.0)
      return 0.0;

   return NormalizeVolumeDown(riskMoney / lossPerLot);
}

double NormalizePriceToTick(const double price)
{
   double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   int digits      = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);

   if(tickSize <= 0.0)
      return NormalizeDouble(price, digits);

   return NormalizeDouble(MathRound(price / tickSize) * tickSize, digits);
}

bool ValidateAndAdjustStops(const ENUM_ORDER_TYPE orderType,
                            const double entry,
                            double &sl,
                            double &tp)
{
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   int brokerStops = (int)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
   double minimumDistance = brokerStops * point;

   if(InpMinimumStopPoints > 0)
      minimumDistance = MathMax(minimumDistance,
                                InpMinimumStopPoints * point);

   double stopDistance = MathAbs(entry - sl);

   if(InpMaximumStopPoints > 0 &&
      stopDistance > InpMaximumStopPoints * point)
   {
      Reject("REJECT_STOP_TOO_WIDE");
      return false;
   }

   if(stopDistance < minimumDistance)
   {
      if(orderType == ORDER_TYPE_BUY)
         sl = entry - minimumDistance;
      else
         sl = entry + minimumDistance;
   }

   double riskDistance = MathAbs(entry - sl);
   if(riskDistance <= 0.0)
      return false;

   if(orderType == ORDER_TYPE_BUY)
      tp = entry + riskDistance * InpTargetRMultiple;
   else
      tp = entry - riskDistance * InpTargetRMultiple;

   sl = NormalizePriceToTick(sl);
   tp = NormalizePriceToTick(tp);

   if(orderType == ORDER_TYPE_BUY && !(sl < entry && tp > entry))
      return false;

   if(orderType == ORDER_TYPE_SELL && !(sl > entry && tp < entry))
      return false;

   return true;
}

//--------------------------------------------------------------------
// Daily protections
//--------------------------------------------------------------------
bool DailyRiskAllowsTrading()
{
   int dailyTrades = GetTodayEntryCount();
   if(InpMaximumDailyTrades > 0 &&
      dailyTrades >= InpMaximumDailyTrades)
   {
      Reject("REJECT_MAXIMUM_DAILY_TRADES");
      return false;
   }

   double capital = InpRiskFromEquity
                  ? AccountInfoDouble(ACCOUNT_EQUITY)
                  : AccountInfoDouble(ACCOUNT_BALANCE);

   double dailyLossLimit =
      capital * InpMaximumDailyLossPercent / 100.0;

   double todayPnl = GetTodayClosedProfit();

   if(InpMaximumDailyLossPercent > 0.0 &&
      todayPnl <= -dailyLossLimit)
   {
      Reject("REJECT_DAILY_LOSS_LIMIT");
      return false;
   }

   datetime lastLossTime = 0;
   int consecutiveLosses = GetConsecutiveLosses(lastLossTime);

   if(InpMaximumConsecutiveLosses > 0 &&
      consecutiveLosses >= InpMaximumConsecutiveLosses)
   {
      Reject("REJECT_MAXIMUM_CONSECUTIVE_LOSSES");
      return false;
   }

   if(lastLossTime > 0 && InpCooldownBarsAfterLoss > 0)
   {
      int shift = iBarShift(_Symbol, InpEntryTimeframe,
                            lastLossTime, false);

      if(shift >= 0 && shift <= InpCooldownBarsAfterLoss)
      {
         Reject("REJECT_COOLDOWN_AFTER_LOSS");
         return false;
      }
   }

   return true;
}

//--------------------------------------------------------------------
// Signal evaluation
//--------------------------------------------------------------------
enum SignalDirection
{
   SIGNAL_NONE  = 0,
   SIGNAL_LONG  = 1,
   SIGNAL_SHORT = -1
};

SignalDirection EvaluateCompletedCandleSignal(double &atrValue)
{
   atrValue = 0.0;

   int m15Needed = MathMax(InpEMASlopeLookback + 2, 6);
   int h1Needed  = MathMax(InpHTFSlopeLookback + 2, 6);

   double fast[], medium[], trend[], htfFast[], htfSlow[];
   double adx[], plusDI[], minusDI[], atr[];
   MqlRates m15Rates[], h1Rates[];

   if(!CopyIndicatorValues(hM15FastEMA, 0, 1, m15Needed, fast) ||
      !CopyIndicatorValues(hM15MediumEMA, 0, 1, m15Needed, medium) ||
      !CopyIndicatorValues(hM15TrendEMA, 0, 1, m15Needed, trend) ||
      !CopyIndicatorValues(hH1FastEMA, 0, 1, h1Needed, htfFast) ||
      !CopyIndicatorValues(hH1SlowEMA, 0, 1, h1Needed, htfSlow) ||
      !CopyIndicatorValues(hADX, 0, 1, 3, adx) ||
      !CopyIndicatorValues(hADX, 1, 1, 3, plusDI) ||
      !CopyIndicatorValues(hADX, 2, 1, 3, minusDI) ||
      !CopyIndicatorValues(hATR, 0, 1, 3, atr) ||
      !GetRates(InpEntryTimeframe, 1, m15Needed, m15Rates) ||
      !GetRates(InpTrendTimeframe, 1, h1Needed, h1Rates))
   {
      Reject("REJECT_INSUFFICIENT_INDICATOR_DATA");
      return SIGNAL_NONE;
   }

   atrValue = atr[0];
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   if(point <= 0.0 || atrValue <= 0.0)
   {
      Reject("REJECT_INVALID_ATR");
      return SIGNAL_NONE;
   }

   double atrPoints = atrValue / point;

   if(InpMinimumATRPoints > 0.0 &&
      atrPoints < InpMinimumATRPoints)
   {
      Reject("REJECT_ATR_TOO_LOW");
      return SIGNAL_NONE;
   }

   if(InpMaximumATRPoints > 0.0 &&
      atrPoints > InpMaximumATRPoints)
   {
      Reject("REJECT_ATR_TOO_HIGH");
      return SIGNAL_NONE;
   }

   if(adx[0] < InpMinimumADX)
   {
      Reject("REJECT_ADX_TOO_LOW");
      return SIGNAL_NONE;
   }

   if(InpMaximumADX > 0.0 && adx[0] > InpMaximumADX)
   {
      Reject("REJECT_ADX_TOO_HIGH");
      return SIGNAL_NONE;
   }

   int m15SlopeIndex = InpEMASlopeLookback;
   int h1SlopeIndex  = InpHTFSlopeLookback;

   bool h1Bull =
      h1Rates[0].close > htfFast[0] &&
      htfFast[0] > htfSlow[0] &&
      htfFast[0] > htfFast[h1SlopeIndex];

   bool h1Bear =
      h1Rates[0].close < htfFast[0] &&
      htfFast[0] < htfSlow[0] &&
      htfFast[0] < htfFast[h1SlopeIndex];

   bool m15Bull =
      fast[0] > medium[0] &&
      medium[0] > trend[0] &&
      m15Rates[0].close > trend[0] &&
      medium[0] > medium[m15SlopeIndex];

   bool m15Bear =
      fast[0] < medium[0] &&
      medium[0] < trend[0] &&
      m15Rates[0].close < trend[0] &&
      medium[0] < medium[m15SlopeIndex];

   // rates[0] = just-closed trigger candle (candle 1)
   // rates[1] = completed pullback candle (candle 2)
   double pullbackBuffer = atrValue * InpPullbackATRBuffer;

   bool longPullbackTouch =
      m15Rates[1].low <= medium[1] + pullbackBuffer &&
      m15Rates[1].high >= fast[1] - pullbackBuffer;

   bool shortPullbackTouch =
      m15Rates[1].high >= medium[1] - pullbackBuffer &&
      m15Rates[1].low <= fast[1] + pullbackBuffer;

   bool bullishRecovery =
      m15Rates[0].close > fast[0] &&
      m15Rates[0].close > m15Rates[0].open &&
      m15Rates[0].close > m15Rates[1].close;

   bool bearishRecovery =
      m15Rates[0].close < fast[0] &&
      m15Rates[0].close < m15Rates[0].open &&
      m15Rates[0].close < m15Rates[1].close;

   if(!InpRequireCandleDirection)
   {
      bullishRecovery =
         m15Rates[0].close > fast[0] &&
         m15Rates[0].close > m15Rates[1].close;

      bearishRecovery =
         m15Rates[0].close < fast[0] &&
         m15Rates[0].close < m15Rates[1].close;
   }

   bool longSignal =
      InpAllowLongs &&
      h1Bull &&
      m15Bull &&
      plusDI[0] > minusDI[0] &&
      longPullbackTouch &&
      bullishRecovery;

   bool shortSignal =
      InpAllowShorts &&
      h1Bear &&
      m15Bear &&
      minusDI[0] > plusDI[0] &&
      shortPullbackTouch &&
      bearishRecovery;

   Log(StringFormat(
      "Signal check | ADX=%.2f +DI=%.2f -DI=%.2f ATR=%.5f "
      "H1Bull=%s H1Bear=%s M15Bull=%s M15Bear=%s "
      "LongPullback=%s ShortPullback=%s",
      adx[0], plusDI[0], minusDI[0], atrValue,
      h1Bull ? "true" : "false",
      h1Bear ? "true" : "false",
      m15Bull ? "true" : "false",
      m15Bear ? "true" : "false",
      longPullbackTouch ? "true" : "false",
      shortPullbackTouch ? "true" : "false"));

   if(longSignal)
      return SIGNAL_LONG;

   if(shortSignal)
      return SIGNAL_SHORT;

   Reject("REJECT_NO_VALID_PULLBACK_SIGNAL");
   return SIGNAL_NONE;
}

//--------------------------------------------------------------------
// Spread protection
//--------------------------------------------------------------------
bool SpreadIsAcceptable(const double atrValue,
                        double &spreadPoints)
{
   MqlTick tick;
   if(!SymbolInfoTick(_Symbol, tick))
   {
      Reject("REJECT_NO_CURRENT_TICK");
      return false;
   }

   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   if(point <= 0.0 || tick.ask <= 0.0 || tick.bid <= 0.0)
   {
      Reject("REJECT_INVALID_MARKET_PRICE");
      return false;
   }

   spreadPoints = (tick.ask - tick.bid) / point;

   if(InpMaximumSpreadPoints > 0 &&
      spreadPoints > InpMaximumSpreadPoints)
   {
      Reject("REJECT_SPREAD_TOO_HIGH_FIXED");
      return false;
   }

   if(InpMaximumSpreadATRPercent > 0.0 && atrValue > 0.0)
   {
      double spreadATRPercent =
         ((tick.ask - tick.bid) / atrValue) * 100.0;

      if(spreadATRPercent > InpMaximumSpreadATRPercent)
      {
         Reject("REJECT_SPREAD_TOO_HIGH_RELATIVE_TO_ATR");
         return false;
      }
   }

   return true;
}

//--------------------------------------------------------------------
// Order execution
//--------------------------------------------------------------------
bool OpenSignalPosition(const SignalDirection signal,
                        const double atrValue)
{
   MqlTick tick;
   if(!SymbolInfoTick(_Symbol, tick))
   {
      Reject("REJECT_NO_CURRENT_TICK");
      return false;
   }

   ENUM_ORDER_TYPE orderType =
      signal == SIGNAL_LONG ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;

   double entry = signal == SIGNAL_LONG ? tick.ask : tick.bid;
   double sl = signal == SIGNAL_LONG
             ? entry - atrValue * InpStopATRMultiplier
             : entry + atrValue * InpStopATRMultiplier;
   double tp = 0.0;

   if(!ValidateAndAdjustStops(orderType, entry, sl, tp))
   {
      Reject("REJECT_INVALID_STOPS");
      return false;
   }

   double volume = CalculateRiskVolume(entry, sl);
   if(volume <= 0.0)
   {
      Reject("REJECT_VOLUME_INVALID_OR_BELOW_BROKER_MINIMUM");
      return false;
   }

   double marginRequired = 0.0;
   if(!OrderCalcMargin(orderType, _Symbol, volume,
                       entry, marginRequired))
   {
      Reject("REJECT_MARGIN_CALCULATION_FAILED");
      return false;
   }

   if(marginRequired > AccountInfoDouble(ACCOUNT_MARGIN_FREE))
   {
      Reject("REJECT_INSUFFICIENT_FREE_MARGIN");
      return false;
   }

   trade.SetExpertMagicNumber(InpMagicNumber);
   trade.SetDeviationInPoints(InpSlippagePoints);
   trade.SetTypeFillingBySymbol(_Symbol);
   trade.SetAsyncMode(false);

   g_orderInProgress = true;

   bool sent = trade.PositionOpen(
      _Symbol,
      orderType,
      volume,
      entry,
      sl,
      tp,
      signal == SIGNAL_LONG
         ? "AustinM15 Pullback Buy"
         : "AustinM15 Pullback Sell"
   );

   g_orderInProgress = false;

   uint retcode = trade.ResultRetcode();

   if(!sent ||
      (retcode != TRADE_RETCODE_DONE &&
       retcode != TRADE_RETCODE_DONE_PARTIAL &&
       retcode != TRADE_RETCODE_PLACED))
   {
      Log(StringFormat(
         "ORDER FAILED | sent=%s retcode=%u description=%s "
         "volume=%.4f entry=%.5f sl=%.5f tp=%.5f",
         sent ? "true" : "false",
         retcode,
         trade.ResultRetcodeDescription(),
         volume, entry, sl, tp));
      return false;
   }

   g_lastEntryBarTime = g_lastBarTime;

   Log(StringFormat(
      "ORDER ACCEPTED | direction=%s volume=%.4f "
      "entry=%.5f sl=%.5f tp=%.5f risk=%.2f%%",
      signal == SIGNAL_LONG ? "LONG" : "SHORT",
      volume, entry, sl, tp,
      MathMin(InpRiskPercent, InpMaximumRiskPercent)));

   return true;
}

//--------------------------------------------------------------------
// Event handlers
//--------------------------------------------------------------------
int OnInit()
{
   if(InpEntryTimeframe != PERIOD_M15)
      Log("Warning: this release was designed and validated for M15.");

   if(InpRiskPercent <= 0.0 ||
      InpRiskPercent > InpMaximumRiskPercent ||
      InpMaximumRiskPercent > 2.0)
   {
      Print("Invalid risk settings. Risk must be positive and the hard cap cannot exceed 2%.");
      return INIT_PARAMETERS_INCORRECT;
   }

   if(InpStopATRMultiplier <= 0.0 ||
      InpTargetRMultiple <= 0.0)
   {
      Print("Stop and target multipliers must be positive.");
      return INIT_PARAMETERS_INCORRECT;
   }

   if(!MarketAndSymbolAreValid())
      return INIT_FAILED;

   hM15FastEMA = iMA(_Symbol, InpEntryTimeframe,
                     InpFastEMA, 0, MODE_EMA, PRICE_CLOSE);
   hM15MediumEMA = iMA(_Symbol, InpEntryTimeframe,
                       InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE);
   hM15TrendEMA = iMA(_Symbol, InpEntryTimeframe,
                      InpTrendEMA, 0, MODE_EMA, PRICE_CLOSE);

   hH1FastEMA = iMA(_Symbol, InpTrendTimeframe,
                    InpHTFFastEMA, 0, MODE_EMA, PRICE_CLOSE);
   hH1SlowEMA = iMA(_Symbol, InpTrendTimeframe,
                    InpHTFSlowEMA, 0, MODE_EMA, PRICE_CLOSE);

   hADX = iADX(_Symbol, InpEntryTimeframe, InpADXPeriod);
   hATR = iATR(_Symbol, InpEntryTimeframe, InpATRPeriod);

   if(hM15FastEMA == INVALID_HANDLE ||
      hM15MediumEMA == INVALID_HANDLE ||
      hM15TrendEMA == INVALID_HANDLE ||
      hH1FastEMA == INVALID_HANDLE ||
      hH1SlowEMA == INVALID_HANDLE ||
      hADX == INVALID_HANDLE ||
      hATR == INVALID_HANDLE)
   {
      Print("Failed to create one or more indicator handles. Error ",
            GetLastError());
      return INIT_FAILED;
   }

   trade.SetExpertMagicNumber(InpMagicNumber);
   trade.SetDeviationInPoints(InpSlippagePoints);
   trade.SetTypeFillingBySymbol(_Symbol);

   g_lastBarTime = iTime(_Symbol, InpEntryTimeframe, 0);

   Log("Initialised successfully on " + _Symbol +
       ". Entries use completed candles only.");
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   if(hM15FastEMA   != INVALID_HANDLE) IndicatorRelease(hM15FastEMA);
   if(hM15MediumEMA != INVALID_HANDLE) IndicatorRelease(hM15MediumEMA);
   if(hM15TrendEMA  != INVALID_HANDLE) IndicatorRelease(hM15TrendEMA);
   if(hH1FastEMA    != INVALID_HANDLE) IndicatorRelease(hH1FastEMA);
   if(hH1SlowEMA    != INVALID_HANDLE) IndicatorRelease(hH1SlowEMA);
   if(hADX          != INVALID_HANDLE) IndicatorRelease(hADX);
   if(hATR          != INVALID_HANDLE) IndicatorRelease(hATR);

   Log(StringFormat("Deinitialised. reason=%d", reason));
}

void OnTick()
{
   if(!IsNewEntryBar())
      return;

   if(g_orderInProgress)
   {
      Reject("REJECT_ORDER_ALREADY_IN_PROGRESS");
      return;
   }

   if(g_lastEntryBarTime == g_lastBarTime)
   {
      Reject("REJECT_DUPLICATE_ENTRY_BAR");
      return;
   }

   if(!TerminalInfoInteger(TERMINAL_CONNECTED))
   {
      Reject("REJECT_TERMINAL_NOT_CONNECTED");
      return;
   }

   if(!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED) ||
      !MQLInfoInteger(MQL_TRADE_ALLOWED))
   {
      Reject("REJECT_AUTOTRADING_NOT_ALLOWED");
      return;
   }

   if(!IsInsideSession())
   {
      Reject("REJECT_OUTSIDE_SESSION");
      return;
   }

   if(InpOnePositionOnly && HasOurOpenPosition())
   {
      Reject("REJECT_EXISTING_POSITION");
      return;
   }

   if(!DailyRiskAllowsTrading())
      return;

   double atrValue = 0.0;
   SignalDirection signal =
      EvaluateCompletedCandleSignal(atrValue);

   if(signal == SIGNAL_NONE)
      return;

   double spreadPoints = 0.0;
   if(!SpreadIsAcceptable(atrValue, spreadPoints))
      return;

   Log(StringFormat("Signal accepted before execution. Spread=%.1f points",
                    spreadPoints));

   OpenSignalPosition(signal, atrValue);
}

void OnTradeTransaction(
   const MqlTradeTransaction &trans,
   const MqlTradeRequest &request,
   const MqlTradeResult &result)
{
   if(trans.type == TRADE_TRANSACTION_DEAL_ADD &&
      trans.deal > 0)
   {
      if(HistoryDealSelect(trans.deal))
      {
         if((ulong)HistoryDealGetInteger(trans.deal, DEAL_MAGIC)
               == InpMagicNumber &&
            HistoryDealGetString(trans.deal, DEAL_SYMBOL)
               == _Symbol)
         {
            ENUM_DEAL_ENTRY entry =
               (ENUM_DEAL_ENTRY)HistoryDealGetInteger(
                  trans.deal, DEAL_ENTRY);

            double profit =
               HistoryDealGetDouble(trans.deal, DEAL_PROFIT)
             + HistoryDealGetDouble(trans.deal, DEAL_SWAP)
             + HistoryDealGetDouble(trans.deal, DEAL_COMMISSION);

            Log(StringFormat(
               "TRADE TRANSACTION | deal=%I64u entry=%d "
               "price=%.5f volume=%.4f result=%.2f",
               trans.deal,
               (int)entry,
               HistoryDealGetDouble(trans.deal, DEAL_PRICE),
               HistoryDealGetDouble(trans.deal, DEAL_VOLUME),
               profit));
         }
      }
   }
}
//+------------------------------------------------------------------+
