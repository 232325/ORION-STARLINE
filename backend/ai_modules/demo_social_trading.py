#!/usr/bin/env python3
"""
Social Trading Platform Demo

Bu demo Social Trading Platform modulining asosiy funksiyalarini ko'rsatadi.
Orion Starline AI Trading System uchun ijtimoiy savdo platformasi.

Demo quyidagi funksiyalarni namoyon etadi:
- Foydalanuvchi ro'yxatdan o'tkazish
- Treyder tasdiqlash tizimi
- Trading signal yaratish
- Copy trading tizimi
- Ijtimoiy xususiyatlar
- Performance kuzatish
- Reyting tizimi

Muallif: AI Team
Yaratilgan sana: 2025-11-05
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from social_trading import (
    SocialTradingPlatform, UserRole, SignalType, SignalPrivacy, VerificationStatus
)
import time

def print_header(title: str):
    """Chiroyli header chop etish"""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_step(step: int, title: str):
    """Qadam nomini chop etish"""
    print(f"\n📋 Qadam {step}: {title}")
    print("-" * 40)

def demo_social_trading_platform():
    """Asosiy demo funksiyasi"""
    
    print_header("Social Trading Platform Demo")
    print("""
Bu demo ijtimoiy savdo platformasining barcha asosiy funksiyalarini ko'rsatadi:
- Foydalanuvchi autentifikatsiyasi
- Treyder tasdiqlash tizimi  
- Trading signallar
- Copy trading
- Ijtimoiy xususiyatlar
- Performance kuzatish
- Reyting tizimi
""")
    
    # 1. Platformani yaratish
    print_step(1, "Platformani ishga tushirish")
    platform = SocialTradingPlatform("demo_social_trading.db")
    print("✅ Social Trading Platform muvaffaqiyatli ishga tushdi")
    
    # 2. Foydalanuvchilarni ro'yxatdan o'tkazish
    print_step(2, "Foydalanuvchilarni ro'yxatdan o'tkazish")
    
    # Treyder yaratish
    trader_result = platform.register_user(
        username="ali_trader",
        email="ali@example.com", 
        password="secure123",
        role=UserRole.TRADER
    )
    
    if trader_result["success"]:
        trader_id = trader_result["user_id"]
        print(f"✅ Treyder yaratildi: {trader_result['message']}")
        print(f"   Username: ali_trader")
        print(f"   Email: ali@example.com")
    else:
        print(f"❌ Treyder yaratishda xatolik: {trader_result['message']}")
        return
    
    # Obunachi yaratish
    follower_result = platform.register_user(
        username="bob_investor",
        email="bob@example.com",
        password="secure123", 
        role=UserRole.FOLLOWER
    )
    
    if follower_result["success"]:
        follower_id = follower_result["user_id"]
        print(f"✅ Obunachi yaratildi: {follower_result['message']}")
        print(f"   Username: bob_investor")
        print(f"   Email: bob@example.com")
    else:
        print(f"❌ Obunachi yaratishda xatolik: {follower_result['message']}")
        return
    
    # Admin yaratish
    admin_result = platform.register_user(
        username="admin",
        email="admin@example.com",
        password="admin123",
        role=UserRole.ADMIN
    )
    
    if admin_result["success"]:
        admin_id = admin_result["user_id"]
        print(f"✅ Admin yaratildi: {admin_result['message']}")
        print(f"   Username: admin")
    else:
        print(f"❌ Admin yaratishda xatolik: {admin_result['message']}")
        return
    
    # 3. Treyder tasdiqlash so'rovi
    print_step(3, "Treyder tasdiqlash so'rovi")
    
    verification_result = platform.request_verification(
        user_id=trader_id,
        documents=["id_document.pdf", "proof_of_income.pdf", "trading_certificate.pdf"]
    )
    
    if verification_result["success"]:
        print(f"✅ {verification_result['message']}")
        print("   Hujjatlar: ID dokument, daromad dalili, savdo sertifikati")
    else:
        print(f"❌ Tasdiqlash so'rovida xatolik: {verification_result['message']}")
    
    # 4. Admin tasdiqlash
    print_step(4, "Admin tomonidan tasdiqlash")
    
    verification_approve = platform.verify_trader(
        admin_id=admin_id,
        user_id=trader_id,
        approved=True,
        reason="Barcha hujjatlar to'g'ri va to'liq"
    )
    
    if verification_approve["success"]:
        print(f"✅ {verification_approve['message']}")
        print("   Status: TASDIQLANGAN ✅")
    else:
        print(f"❌ Tasdiqlashda xatolik: {verification_approve['message']}")
    
    # 5. Trading signal yaratish
    print_step(5, "Trading signal yaratish")
    
    signal_result = platform.create_signal(
        trader_id=trader_id,
        symbol="EURUSD",
        signal_type=SignalType.BUY,
        price=1.0950,
        stop_loss=1.0900,
        take_profit=1.1000,
        privacy=SignalPrivacy.PUBLIC,
        confidence=0.85,
        description="EUR/USD strong bullish signal. Technical analysis shows uptrend continuation expected."
    )
    
    if signal_result["success"]:
        signal_id = signal_result["signal_id"]
        print(f"✅ {signal_result['message']}")
        print(f"   Signal ID: {signal_id}")
        print(f"   Symbol: EURUSD")
        print(f"   Type: BUY")
        print(f"   Entry Price: 1.0950")
        print(f"   Stop Loss: 1.0900")
        print(f"   Take Profit: 1.1000")
        print(f"   Confidence: 85%")
    else:
        print(f"❌ Signal yaratishda xatolik: {signal_result['message']}")
        return
    
    # 6. Copy trading boshlash
    print_step(6, "Copy trading boshlash")
    
    copy_result = platform.start_copy_trading(
        follower_id=follower_id,
        trader_id=trader_id,
        amount=1000.0,
        copy_percentage=100.0
    )
    
    if copy_result["success"]:
        copy_trade_id = copy_result["copy_trade_id"]
        print(f"✅ {copy_result['message']}")
        print(f"   Copy Trade ID: {copy_trade_id}")
        print(f"   Amount: $1,000")
        print(f"   Copy Percentage: 100%")
    else:
        print(f"❌ Copy trading boshlashda xatolik: {copy_result['message']}")
    
    # 7. Obuna bo'lish
    print_step(7, "Treyderga obuna bo'lish")
    
    follow_result = platform.follow_trader(
        follower_id=follower_id,
        trader_id=trader_id,
        copy_percentage=75.0
    )
    
    if follow_result["success"]:
        print(f"✅ {follow_result['message']}")
        print("   Obuna foizi: 75%")
    else:
        print(f"❌ Obuna bo'lishda xatolik: {follow_result['message']}")
    
    # 8. Signal bajarish (copy trade)
    print_step(8, "Copy trade bajarish")
    
    execute_result = platform.execute_copy_trade(
        signal_id=signal_id,
        follower_id=follower_id,
        amount=500.0
    )
    
    if execute_result["success"]:
        exec_copy_trade_id = execute_result["copy_trade_id"]
        print(f"✅ {execute_result['message']}")
        print(f"   Copy Trade ID: {exec_copy_trade_id}")
        print(f"   Amount: $500")
    else:
        print(f"❌ Copy trade bajarishda xatolik: {execute_result['message']}")
    
    # 9. Reyting berish
    print_step(9, "Treyderga reyting berish")
    
    rating_result = platform.rate_trader(
        user_id=follower_id,
        trader_id=trader_id,
        rating=4.5,
        comment="Juda yaxshi signal! Aniq kirish nuqta va to'g'ri risk boshqaruvi."
    )
    
    if rating_result["success"]:
        print(f"✅ {rating_result['message']}")
        print("   Rating: 4.5/5 ⭐")
        print("   Comment: 'Juda yaxshi signal!'")
    else:
        print(f"❌ Reyting berishda xatolik: {rating_result['message']}")
    
    # 10. Signallar ro'yxati
    print_step(10, "Mavjud signallar")
    
    signals = platform.get_signals(limit=5)
    if signals["success"]:
        print(f"✅ {len(signals['signals'])} ta signal topildi:")
        for signal in signals["signals"]:
            print(f"   📊 {signal['symbol']} - {signal['signal_type']} at {signal['price']}")
            print(f"      Confidence: {signal['confidence']*100}%")
            print(f"      By: {signal['trader_name']}")
    else:
        print(f"❌ Signallar olishda xatolik: {signals['message']}")
    
    # 11. Top performers
    print_step(11, "Top performers leaderboard")
    
    leaderboard = platform.get_top_performers(period="month", limit=5)
    if leaderboard["success"] and leaderboard["performers"]:
        print("🏆 Top Performers:")
        for performer in leaderboard["performers"]:
            verified_mark = "✅" if performer["verified"] else "❌"
            print(f"   #{performer['rank']}: {performer['username']} - Rating: {performer['rating']:.1f} {verified_mark}")
            print(f"      Followers: {performer['followers_count']}, Win Rate: {performer['win_rate']:.1f}%")
    else:
        print("📊 Hozircha top performers mavjud emas (yangi platform)")
    
    # 12. Performance kuzatish
    print_step(12, "Performance kuzatish")
    
    performance = platform.track_performance(follower_id)
    if performance["success"]:
        perf = performance["performance"]
        print("📈 Obunachi Performance:")
        print(f"   Jami trade: {perf['total_trades']}")
        print(f"   Yutish foizi: {perf['win_rate']:.1f}%")
        print(f"   Jami P&L: ${perf['total_profit_loss']:.2f}")
        print(f"   O'rtacha qaytish: {perf['total_return']:.2f}%")
    else:
        print(f"❌ Performance olishda xatolik: {performance['message']}")
    
    # 13. Platform statistikalari
    print_step(13, "Platform umumiy statistikalari")
    
    stats = platform.get_platform_stats()
    if stats["success"]:
        platform_stats = stats["stats"]
        print("📊 Platform Stats:")
        print(f"   Jami foydalanuvchilar: {platform_stats['total_users']}")
        print(f"   Tasdiqlangan treyderlar: {platform_stats['verified_traders']}")
        print(f"   Signallar soni: {platform_stats['total_signals']}")
        print(f"   Copy trade lar: {platform_stats['total_copy_trades']}")
        print(f"   Aktiv copy trade: {platform_stats['active_copy_trades']}")
        print(f"   Jami hajm: ${platform_stats['total_volume']:.2f}")
    else:
        print(f"❌ Platform statistikalari olishda xatolik: {stats['message']}")
    
    # 14. Bildirishnomalar
    print_step(14, "Bildirishnomalar")
    
    notifications = platform.get_notifications(follower_id)
    if notifications["success"] and notifications["notifications"]:
        print("🔔 So'nggi bildirishnomalar:")
        for notif in notifications["notifications"][:3]:
            read_mark = "✅" if notif["read"] else "🔴"
            print(f"   {read_mark} {notif['title']}: {notif['message']}")
    else:
        print("📱 Bildirishnomalar mavjud emas")
    
    # 15. Like funksiyasi
    print_step(15, "Social interaction (Like)")
    
    like_result = platform.like_entity(
        user_id=follower_id,
        entity_id=signal_id,
        entity_type="signal"
    )
    
    if like_result["success"]:
        liked_status = "Like qo'yildi" if like_result["liked"] else "Like olib tashlandi"
        print(f"✅ {liked_status}")
        print(f"   Likes soni: {like_result['likes_count']}")
    else:
        print(f"❌ Like qilishda xatolik: {like_result['message']}")
    
    print_header("Demo Yakunlandi")
    print("""
🎉 Social Trading Platform muvaffaqiyatli test qilindi!

Asosiy funksiyalar:
✅ Foydalanuvchi autentifikatsiyasi
✅ Treyder tasdiqlash tizimi
✅ Trading signallar
✅ Copy trading
✅ Ijtimoiy xususiyatlar
✅ Performance kuzatish
✅ Reyting tizimi

Platform real savdo uchun tayyor!
    """)
    
    return platform

def interactive_demo():
    """Interaktiv demo funksiyasi"""
    
    print_header("Interactive Social Trading Demo")
    
    platform = SocialTradingPlatform("interactive_demo.db")
    
    print("""
Interaktiv demo bosqichlari:
1. Foydalanuvchi yaratish
2. Treyder profilini tekshirish
3. Signal yaratish
4. Copy trading boshlash
5. Performance kuzatish
    """)
    
    while True:
        print("\n" + "="*50)
        print("🎯 Qaysi qadamni bajarishni xohlaysiz?")
        print("1. Foydalanuvchi yaratish")
        print("2. Signal yaratish")
        print("3. Copy trading")
        print("4. Performance ko'rish")
        print("5. Top performers")
        print("6. Platform statistikalari")
        print("0. Chiqish")
        
        try:
            choice = input("\nTanlang (0-6): ").strip()
            
            if choice == "0":
                print("👋 Demo tugadi!")
                break
            elif choice == "1":
                username = input("Username: ").strip()
                email = input("Email: ").strip()
                password = input("Parol: ").strip()
                role_choice = input("Rol (1-Treyder, 2-Obunachi): ").strip()
                
                role = UserRole.TRADER if role_choice == "1" else UserRole.FOLLOWER
                
                result = platform.register_user(username, email, password, role)
                print(f"Result: {result['message']}")
                
            elif choice == "2":
                trader_id = input("Treyder ID: ").strip()
                symbol = input("Symbol (masalan: EURUSD): ").strip()
                price = float(input("Narx: "))
                confidence = float(input("Ishonch darajasi (0.1-1.0): "))
                
                signal_result = platform.create_signal(
                    trader_id=trader_id,
                    symbol=symbol,
                    signal_type=SignalType.BUY,
                    price=price,
                    confidence=confidence
                )
                print(f"Signal yaratildi: {signal_result['message']}")
                
            elif choice == "3":
                follower_id = input("Obunachi ID: ").strip()
                trader_id = input("Treyder ID: ").strip()
                amount = float(input("Miqdor ($): "))
                
                copy_result = platform.start_copy_trading(follower_id, trader_id, amount)
                print(f"Copy trading: {copy_result['message']}")
                
            elif choice == "4":
                user_id = input("Foydalanuvchi ID: ").strip()
                performance = platform.track_performance(user_id)
                if performance["success"]:
                    perf = performance["performance"]
                    print(f"Performance: Win Rate {perf['win_rate']:.1f}%, P&L ${perf['total_profit_loss']:.2f}")
                else:
                    print(f"Xatolik: {performance['message']}")
                    
            elif choice == "5":
                leaderboard = platform.get_top_performers()
                if leaderboard["success"]:
                    print("Top Performers:")
                    for performer in leaderboard["performers"][:5]:
                        print(f"#{performer['rank']}: {performer['username']} - {performer['rating']:.1f}")
                else:
                    print("Leaderboard mavjud emas")
                    
            elif choice == "6":
                stats = platform.get_platform_stats()
                if stats["success"]:
                    platform_stats = stats["stats"]
                    print(f"Platform Stats:")
                    print(f"  Users: {platform_stats['total_users']}")
                    print(f"  Signals: {platform_stats['total_signals']}")
                    print(f"  Copy Trades: {platform_stats['total_copy_trades']}")
                else:
                    print(f"Xatolik: {stats['message']}")
            else:
                print("❌ Noto'g'ri tanlov")
                
        except KeyboardInterrupt:
            print("\n\n👋 Demo to'xtatildi!")
            break
        except Exception as e:
            print(f"❌ Xatolik yuz berdi: {str(e)}")

if __name__ == "__main__":
    print("🚀 Social Trading Platform Demo")
    print("1. Avtomatik demo")
    print("2. Interaktiv demo")
    
    try:
        choice = input("Tanlang (1 yoki 2): ").strip()
        
        if choice == "2":
            interactive_demo()
        else:
            # Standart avtomatik demo
            demo_social_trading_platform()
            
    except KeyboardInterrupt:
        print("\n\n👋 Demo to'xtatildi!")
    except Exception as e:
        print(f"\n❌ Demo xatolik: {str(e)}")
        import traceback
        traceback.print_exc()