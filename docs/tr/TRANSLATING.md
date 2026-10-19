# Yerelleştirme

*Bu sayfa yapay zekâ yardımıyla çevrildi. Türkçe ana dilinse bir pull request açarak sayfayı geliştirmemize yardım edebilirsin. Referans olarak [İngilizce sürüm](../../localization/README.md) geçerlidir.*

Ebbtide'ın arayüz metinleri, çeviriye hazır. Oyun Korece yazılıyor. Diğer tüm diller için kaynak İngilizce.

## Klasörler

Aşağıdaki yollar [`localization/`](../../localization/) klasörünün içindedir.

| Yol | İçeriği |
| --- | --- |
| `source/strings/<Table>.csv` | Oyundaki güncel metinler: `key`, `en`, `ko`. Düzenleme; oyundan yeniden üretilir. |
| `source/SNAPSHOT` | Güncel kaynak anlık görüntüsünün tarihi ve boyutu |
| `translations/<lang>/<Table>.csv` | Her dil için bir klasör: `key`, `en`, `translation`, `status` |
| `glossary.csv` | İsimler, askerî terimler ve bunların nasıl ele alınacağı |

Dil klasörleri `de`, `fr`, `pt-BR`, `ro`, `zh-Hans` gibi kodlar kullanır. Türkçenin kodu `tr`.

## Nasıl çevrilir

1. Dilin için bir [çevirmen issue'su](https://github.com/Epheria/Ebbtide-Community/issues/new?template=translator.yml) aç. Dil klasörünü bir proje sorumlusu (maintainer) oluşturur.
2. `translations/<lang>/` içindeki dosyaları düzenle. Yalnızca `translation` sütununu doldur.
3. Tüm yer tutucuları İngilizcedeki gibi aynen koru: `{0}`, `{1}`, `<b>` gibi zengin metin etiketleri ve `\n` satır sonları. Bunların cümle içindeki yerini değiştirebilirsin.
4. İsimler ve terimler için `glossary.csv` dosyasına bak.
5. Bir pull request aç. Otomatik bir kontrol, eksik yer tutucuları ya da bozuk satırları bildirir.

Emin olmadığın bir satırın `translation` alanını boş bırak. Boş satırlar oyunda İngilizce görünür.

### CSV dosyalarını düzenleme

- Küçük değişiklikler için GitHub'ın web düzenleyicisi yeterli.
- Daha büyük işler için LibreOffice Calc ya da Google Sheets kullan. Dosyayı UTF-8 ve virgül ayırıcıyla içe aktar. Sonra aynı dört sütunla, UTF-8 CSV olarak dışa aktar.
- "CSV UTF-8" olarak kaydetmeyeceksen Microsoft Excel'den uzak dur. Diğer biçimler İngilizce dışı karakterleri (ç, ğ, ı, ş gibi) bozar.

## `status` sütunu

| Değer | Anlamı | Ne yapmalı |
| --- | --- | --- |
| (boş) | Sorun yok ya da henüz çevrilmedi | Boşsa çevir |
| `outdated` | İngilizce metin, çevrildikten sonra değişti | Çeviriyi güncelle, sonra durumu temizle |
| `review` | Bir inceleyici tekrar bakmak istiyor | Pull request'te tartış |

## Oyun metni değiştiğinde

Oyun hâlâ geliştiriliyor. Bu yüzden İngilizce metinler sık sık eklenir, değişir ve silinir. Kaynak güncellendiğinde bir proje sorumlusu `python tools/l10n.py update` komutunu çalıştırır. Bu komut:

- yeni satırları boş bir çeviriyle ekler,
- İngilizcesi değişen satırları `outdated` olarak işaretler ve eski çevirini korur,
- oyunda artık olmayan satırları kaldırır.

## Proje sorumluları için

```bash
python tools/export_unity_strings.py --project <path to the Unity project>  # refresh the source (needs PyYAML)
python tools/l10n.py update                                                 # sync every language
python tools/l10n.py init <lang>                                            # open a new language
python tools/l10n.py check                                                  # the same check the pull requests run
python tools/l10n.py status                                                 # progress per language
```

Hikâye sahneleri (ara sahne diyalogları) henüz dahil değil. Senaryo kesinleşince eklenecekler.
