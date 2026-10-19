# Seslendirme

> **Yazılı çeviri ve ses kaydı ayrı ilerler:** Senaryo çevirileri için [Türkçe iş akışı kılavuzunu](CONTRIBUTION_WORKFLOW.md) kullan. `voice-text` görevi ve incelenen kopyanın onayı yalnızca yazılı replikleri kapsar. Aşağıdaki seçme, rol dağıtımı ve ses dosyası teslim adımları kayıtlar içindir; metnin onaylanması tek başına kayda başlama izni değildir.

*Bu sayfa yapay zekâ yardımıyla çevrildi. Türkçe ana dilinse bir pull request açarak sayfayı geliştirmemize yardım edebilirsin. Referans olarak [İngilizce sürüm](../../voice/README.md) geçerlidir.*

Ebbtide'daki tüm replikler şu an yapay zekâ ile seslendiriliyor. Hepsinin yerini gerçek seslendirme sanatçıları alacak: pilotlar, helikopter mürettebatı, gemi subayları, araç mürettebatı ve piyade timleri.

## Nasıl işliyor

1. **Seçme.** Discord'daki gönderim (submissions) kanalına kısa bir kayıt at. Kanalda sabitlenmiş örnek replikleri oku.
2. **Rol dağıtımı.** Sesin bir role uyuyorsa bir proje sorumlusu (maintainer) seninle iletişime geçer ve özel bir ticket açar.
3. **Senaryo.** Rolünün tam senaryosu `scripts/<role>.csv` dosyasına eklenir: dosya adı, durum, ton ve replik.
4. **Teslim.** Kayıtları size ayrılan özel Drive klasörüne yükleyin ve çalışma sayfanızda `Ready to submit` kutularını işaretleyin. Her replik ayrı bir dosya olmalı ve adı senaryodakiyle aynı olmalıdır. [Kayıt teslim kılavuzunu (İngilizce)](../VOICE_SUBMISSIONS.md) izleyin. Ses dosyalarını herkese açık PR’a eklemeyin.
5. **İnceleme.** Kayıtları dinleriz, gerekirse yeniden kayıt isteriz, birleştiririz ve replikleri bir sonraki sürüme ekleriz.

Mevcut senaryolar: [`voice/scripts/`](../../voice/scripts/). Ses dosyaları özel Drive klasöründe saklanır.

## Kayıt özellikleri

Temiz ve kuru (efektsiz) kaydet. Telsiz efektlerini oyun kendisi ekliyor.

- Tercihen FLAC (daha küçük), ya da WAV. Mono, 48 kHz, 24-bit (44,1 kHz / 16-bit de olur).
- Reverb, efekt, müzik ya da telsiz filtresi yok.
- Sessiz bir oda: yankı ya da arka plan gürültüsü olmasın.
- En yüksek tepeler yaklaşık -3 dB civarında olsun, asla clipping (patlama) olmasın.
- Her dosyada tek replik olsun; öncesinde ve sonrasında yaklaşık yarım saniye sessizlik bırak.

## Bir şey göndermeden önce

[CONTRIBUTOR_TERMS.md](../../CONTRIBUTOR_TERMS.md) dosyasını, özellikle ses kayıtlarıyla ilgili kısmı oku. Bu dosya İngilizcedir; resmî metin İngilizce olandır. 18 yaşından küçüksen bir ebeveynin ya da vasinin de seninle birlikte onay vermesi gerekir.
