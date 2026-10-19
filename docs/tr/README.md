# Ebbtide Topluluğu

> **Çevirmenler için not:** Arayüz ve seslendirme metni çevirileri için bir proje sorumlusunun görev ataması ve çeviriyi başka bir kişinin incelemesi gerekir. Sana atanan Google E-Tablolar dosyasında çalış; incelemeden sonra bot pull request açar. Önce İngilizce [iş akışını](../CONTRIBUTION_WORKFLOW.md) oku. Aşağıdaki Git ile doğrudan gönderim adımları diğer katkılar içindir; dosya biçimi açıklamalarından yararlanmaya devam edebilirsin.

*Bu sayfa yapay zekâ yardımıyla çevrildi. Türkçe ana dilinse bir pull request açarak sayfayı geliştirmemize yardım edebilirsin. Referans olarak [İngilizce sürüm](../../README.md) geçerlidir.*

[English](../../README.md) · [Español](../es/README.md) · [Русский](../ru/README.md) · [한국어](../ko/README.md) · [日本語](../ja/README.md) · [Polski](../pl/README.md) · **Türkçe** · [Français](../fr/README.md)

Burası, topluluğun Ebbtide'ı birlikte geliştirdiği yer: çeviriler, seslendirme ve oyuna giren diğer katkılar.

Ebbtide, tek bir geliştiricinin yaptığı, gerçek zamanlı komuta içeren, tepeden bakışlı bir zombi hayatta kalma oyunu. Oyunun birçok parçası yapay zekâyla üretilmiş sesler, müzikler ve çevirilerle başladı. Bu deponun amacı, bunları parça parça topluluktaki gerçek insanların emeğiyle değiştirmek.

## Nasıl yardım edebilirsin

| Alan | Nasıl başlanır | Çalışma nereye gider |
| --- | --- | --- |
| Çeviri | Bir [çevirmen issue'su](https://github.com/Epheria/Ebbtide-Community/issues/new?template=translator.yml) aç, sonra [çeviri rehberini](TRANSLATING.md) oku | [`localization/`](../../localization/) |
| Seslendirme | Discord'daki gönderim (submissions) kanalında seçmelere katıl ya da bir [seslendirme sanatçısı issue'su](https://github.com/Epheria/Ebbtide-Community/issues/new?template=voice_actor.yml) aç. Ayrıntılar: [seslendirme rehberi](VOICE.md) | [`voice/`](../../voice/) |
| Müzik, ses ve görsel | Önce çalışmanı Discord'daki gönderim kanalında paylaş | Çalışma seçilince bir klasör eklenir |
| Oyun testi geri bildirimi | Oyun testi açılınca katıl ve geri bildirimini Discord'da paylaş | Bu depoda değil |

## Katkın oyuna nasıl girer

1. Bir issue ile başvur ya da Discord'daki gönderim kanalından seçil.
2. [CONTRIBUTOR_TERMS.md](../../CONTRIBUTOR_TERMS.md) dosyasını oku (bu dosya İngilizcedir; resmî metin İngilizce olandır). Çalışmanın sahibi sen olmaya devam edersin; yalnızca Ebbtide'da kullanılmasına izin verirsin.
3. Bu depoyu fork'la, çalışmanı ekle ve bir pull request aç.
4. Çevirilerde otomatik kontroller çalışır, ardından bir inceleyici pull request'ine bakar.
5. Onaylanan çalışma burada birleştirilir (merge) ve geliştirici onu bir sonraki sürüme ekler.

Katkıda bulunan herkes, seçtiği isimle oyunun emeği geçenler listesinde yer alır.

## Temel kurallar

- Yalnızca kendi özgün çalışmanı gönder.
- Yapay zekâyla üretilmiş çeviri, ses, müzik ya da görsel yok. Bütün mesele gerçek insanların emeği.
- İncelemelerde nazik ol. Buradakilerin çoğu gönüllü.

Ayrıntılar için [CONTRIBUTING.md](CONTRIBUTING.md) sayfasına bak.

## Durum

- Çeviri: açık. İngilizce kaynak metin, hâlâ geliştirilen bir oyunun anlık görüntüsü; yani metinler değişecek. Değişen satırlar otomatik olarak işaretlenir.
- Seslendirme: önce seçmeler. 21 rolün tamamının senaryoları [`voice/scripts/`](../../voice/scripts/) klasöründe.
