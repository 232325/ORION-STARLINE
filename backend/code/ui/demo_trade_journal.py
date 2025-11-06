"""
Trade Journal Demo
==================

Trade journal modulining barcha funksiyalarini namoyish qilish
"""

import asyncio
from datetime import datetime, timedelta
from trade_journal import (
    TradeJournal, 
    JournalEntry, 
    TradeSetup, 
    TradeOutcome, 
    EmotionalState
)


async def demo_all_features():
    """Trade journal barcha imkoniyatlarini namoyish"""
    
    print("=" * 60)
    print("TRADE JOURNAL MODULI - TO'LIQ DEMO")
    print("=" * 60)
    
    # Yangi journal yaratish
    journal = TradeJournal()
    
    # 1. Yangi entry qo'shish
    print("\n1. YANGI ENTRY QO'SHISH")
    print("-" * 30)
    
    new_entry = JournalEntry(
        entry_id="demo_001",
        trade_id="trade_demo_001",
        symbol="BTC/USDT",
        side="long",
        entry_date=datetime.now() - timedelta(hours=2),
        exit_date=datetime.now(),
        entry_price=45000.0,
        exit_price=46500.0,
        size=0.1,
        pnl=150.0,
        pnl_percent=3.33,
        setup=TradeSetup.BREAKOUT,
        strategy_name="M15 Breakout Strategy",
        timeframe="15m",
        entry_reason="Strong volume breakout with RSI confirmation",
        exit_reason="Reached target resistance level",
        notes="Perfect execution. Followed the plan completely. Entry was clean and exit was timely.",
        lessons_learned="Always wait for volume confirmation on breakouts",
        tags=["breakout", "high-confidence", "btc"],
        emotional_state_entry=EmotionalState.CONFIDENT,
        emotional_state_exit=EmotionalState.CALM,
        outcome=TradeOutcome.BIG_WIN,
        mistakes=[],
        what_went_well=["Good risk management", "Patient entry", "Clean exit"],
        what_to_improve=[],
        reviewed=True,
        review_date=datetime.now() - timedelta(minutes=30),
        review_notes="Excellent trade. Perfect example of proper breakout trading."
    )
    
    entry_id = await journal.add_entry(new_entry)
    print(f"✓ Entry qo'shildi: {entry_id}")
    
    # 2. Entry olish
    print("\n2. ENTRY OLISH")
    print("-" * 30)
    
    retrieved_entry = await journal.get_entry(entry_id)
    if retrieved_entry:
        print(f"✓ Entry topildi: {retrieved_entry.symbol}")
        print(f"  Setup: {retrieved_entry.setup.value}")
        print(f"  Natija: {retrieved_entry.outcome.value}")
        print(f"  PnL: ${retrieved_entry.pnl:.2f}")
    
    # 3. Entry yangilash
    print("\n3. ENTRY YANGILASH")
    print("-" * 30)
    
    updated_entry = await journal.update_entry(
        entry_id,
        {"notes": "Updated notes: Great trade execution!", "reviewed": True}
    )
    print(f"✓ Entry yangilandi: {updated_entry.notes}")
    
    # 4. Qidiruv va filtr
    print("\n4. QIDIRUV VA FILTR")
    print("-" * 30)
    
    # Breakout setup bo'yicha qidiruv
    breakout_trades = await journal.search_entries(
        setup=TradeSetup.BREAKOUT,
        limit=5
    )
    print(f"✓ Breakout setup: {len(breakout_trades)} ta savdo topildi")
    
    # Yuqori PnL li savdolar
    profitable_trades = await journal.search_entries(
        min_pnl=100,
        sort_by="pnl",
        limit=5
    )
    print(f"✓ Yuqori PnL (>$100): {len(profitable_trades)} ta savdo")
    
    # BTC/USDT savdolari
    btc_trades = await journal.search_entries(
        symbol="BTC",
        limit=5
    )
    print(f"✓ BTC/USDT savdolar: {len(btc_trades)} ta")
    
    # 5. Statistikalar
    print("\n5. STATISTIKALAR")
    print("-" * 30)
    
    stats = await journal.get_statistics()
    print(f"📊 Jami savdolar: {stats.total_entries}")
    print(f"📊 Ko'rilgan: {stats.reviewed_trades}")
    print(f"📊 Ko'rilmagan: {stats.unreviewed_trades}")
    print(f"📊 Sharhlangan foiz: {(stats.reviewed_trades/stats.total_entries*100):.1f}%")
    
    print("\nSetup taqsimoti:")
    for setup, count in stats.setup_distribution.items():
        print(f"  - {setup}: {count} ta")
    
    print("\nEng yaxshi setup'lar:")
    for setup, avg_pnl in stats.best_performing_setups[:3]:
        print(f"  - {setup}: ${avg_pnl:.2f} o'rtacha")
    
    # 6. Insights
    print("\n6. TRADING INSIGHTS")
    print("-" * 30)
    
    insights = await journal.get_insights()
    print("Win rate by setup:")
    for setup, win_rate in insights['win_rate_by_setup'].items():
        print(f"  - {setup}: {win_rate:.1%}")
    
    print("\nEng yaxshi trading soatlari:")
    for hour, avg_pnl in insights['best_trading_hours'][:3]:
        print(f"  - {hour:02d}:00: ${avg_pnl:.2f} o'rtacha")
    
    # 7. Hisobot yaratish
    print("\n7. HISOBOT YARATISH")
    print("-" * 30)
    
    # Text hisobot
    text_report = await journal.generate_report(format_type="text")
    print("✓ Text hisobot yaratildi (500 belgi ko'rsatiladi):")
    print(text_report[:500] + "...")
    
    # 8. Export qilish
    print("\n8. EXPORT QILISH")
    print("-" * 30)
    
    # CSV export
    csv_file = await journal.export_entries(format_type="csv", filename="demo_trades.csv")
    print(f"✓ CSV eksport: {csv_file}")
    
    # JSON export
    json_file = await journal.export_entries(format_type="json", filename="demo_trades.json")
    print(f"✓ JSON eksport: {json_file}")
    
    # 9. Review tizimi
    print("\n9. REVIEW TIZIMI")
    print("-" * 30)
    
    unreviewed = await journal.search_entries(reviewed=False, limit=5)
    print(f"✓ Ko'rilmagan savdolar: {len(unreviewed)} ta")
    
    if unreviewed:
        # Birinchi ko'rilmagan savdoni review qilish
        first_unreviewed = unreviewed[0]
        reviewed_entry = await journal.mark_as_reviewed(
            first_unreviewed.entry_id,
            review_notes="Good trade, followed the plan well"
        )
        print(f"✓ Review qilindi: {reviewed_entry.entry_id}")
    
    # 10. Pattern recognition
    print("\n10. PATTERN VA TAHLIL")
    print("-" * 30)
    
    # Xatolar tahlili
    print("Eng ko'p uchragan xatolar:")
    for mistake, count in stats.most_common_mistakes[:3]:
        print(f"  - {mistake}: {count} marta")
    
    # Tag tahlili
    print("\nEng popular tag'lar:")
    for tag, count in stats.top_tags[:5]:
        print(f"  - {tag}: {count} marta")
    
    print("\n" + "=" * 60)
    print("DEMO TUGADI - TRADE JOURNAL TO'LIQ ISHLAYAPTI!")
    print("=" * 60)


async def demo_advanced_features():
    """Advansed xususiyatlarni namoyish"""
    
    print("\n" + "=" * 60)
    print("ADVANCED FEATURES DEMO")
    print("=" * 60)
    
    journal = TradeJournal()
    
    # Emotsional tahlil
    print("\n📈 EMOTSIONAL TAHLIL")
    insights = await journal.get_insights()
    
    if insights['emotion_impact']:
        print("Emotsiya ta'siri (o'rtacha PnL):")
        for emotion, avg_pnl in insights['emotion_impact'].items():
            print(f"  - {emotion}: ${avg_pnl:.2f}")
    
    # Setup performance analysis
    print("\n🎯 SETUP PERFORMANCE")
    stats = await journal.get_statistics()
    
    if stats.best_performing_setups:
        best_setup = stats.best_performing_setups[0]
        print(f"Eng foydali setup: {best_setup[0]} (${best_setup[1]:.2f} o'rtacha)")
    
    # Sharhlash stavkasi
    total = stats.total_entries
    reviewed = stats.reviewed_trades
    review_rate = (reviewed / total * 100) if total > 0 else 0
    
    print(f"\n📝 REVIEW STATISTIKA")
    print(f"Sharhlash stavkasi: {review_rate:.1f}%")
    print(f"Ko'rilmagan savdolar: {total - reviewed} ta")


if __name__ == "__main__":
    # Asosiy demo
    asyncio.run(demo_all_features())
    
    # Advanced features demo
    asyncio.run(demo_advanced_features())
    
    print("\n🎉 Trade Journal moduli muvaffaqiyatli test qilindi!")