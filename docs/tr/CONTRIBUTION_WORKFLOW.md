# Çeviri görevleri nasıl yürütülür?

Farklılık olması hâlinde [İngilizce asıl kılavuz](../CONTRIBUTION_WORKFLOW.md) esas alınır. Ana dili Türkçe olan kişilerin ifade düzeltmelerini bekliyoruz. Bot birebir okuduğu için komutlar, issue alan adları, CSV başlıkları ve durum değerleri İngilizce kalır.

Bu kılavuzdaki komutları, sana atanan GitHub görev issue'suna yorum olarak yaz. Komutun İngilizce yazımını aynen koru.

## Genel bakış

Çeviriyi Google E-Tablolar'da yazıp inceleriz. GitHub'daki görev kaydı, işin kapsamını ayırır, kimin sorumlu olduğunu kaydeder ve onaylanan kopyanın pull request'e (PR) dönüşmesini sağlar.

**Tabloyu düzenlemek depoyu veya oyunu güncellemez.** Bot incelenmiş belirli bir kopyayı PR olarak aktarır. Proje sorumlusu PR'ı kontrol edip birleştirir; geliştirici daha sonra sonucu bir oyun sürümüne ekler.

Bu süreç mevcut arayüz metinleri ve seslendirme senaryolarının yazılı çevirileri içindir. Ses kayıtları, seçmeler, yeni replik taslakları ve kaynak kimliği olmayan metinler ayrı hazırlanır. Topluluk çevirileri teslim PR'ını bu botla açar. Elle açılan bir çeviri PR'ı görev ayırma ve kopya onayını atlayamaz.

## Kim ne yapar?

- **Katkıcı:** Atanan çeviriyi tabloda yazar ve önizleme ister.
- **İnceleyici:** Bağlamı, terimleri, doğal anlatımı ve önizlemenin kendisini kontrol eder; kendi GitHub hesabından özet değerini onaylar.
- **Proje sorumlusu (maintainer):** Görevi oluşturur veya kontrol eder, kapsamı ayırır, tablo erişimlerini yönetir, çıkan PR'ı inceler ve birleştirir.

Katkıcı ve inceleyici farklı GitHub kullanıcıları olmalıdır. Bot kimliği ve dosya yapısını kontrol eder; Türkçenin doğal olup olmadığını belirlemez. Çeviri için Git kurmak, depoyu klonlamak veya kendi PR'ını açmak gerekmez; Google E-Tablolar yeterlidir. Onay veren kişinin GitHub hesabı olmalıdır. GitHub yorumlarında yardıma ihtiyaç duyan katkıcı adına bir proje sorumlusu önizleme isteyebilir.

## 1. Küçük bir görev üzerinde anlaşın

Mevcut çevirmen issue'su veya Discord destek ticket'ı üzerinden başvur. İş başlamadan proje sorumlusu dil, katkıcı, inceleyici ve kapsamı netleştirir. Özel başvuru tablosu yalnızca başvuruları toplar; görev ayırmaz. İçeriğini herkese açık GitHub issue'larına kopyalama.

Bir [Translation work order](https://github.com/Epheria/Ebbtide-Community/issues/new?template=work_order.yml) issue'su aç ve İngilizce alan adlarını değiştirmeden doldur:

| Alan | Girilecek bilgi |
| --- | --- |
| Kind | `ui` veya `voice-text` |
| Locale | Depodaki dil kodu; örneğin `tr`, `ja` veya `pt-BR` |
| Table or voice role | Var olan kaynak tablonun veya seslendirme rolünün adı; yol ve `.csv` uzantısı olmadan |
| Contributor | `@` içermeyen tek bir GitHub kullanıcı adı |
| Reviewer | `@` içermeyen, katkıcıdan farklı bir GitHub kullanıcı adı |
| Spreadsheet URL | Bu görev için kullanılan Google E-Tablolar dosyasının adresi |
| Sheet tab | Sekmenin tam adı |
| First key | Dahil edilecek ilk mevcut kaynak anahtarı |
| Last key | Dahil edilecek son mevcut kaynak anahtarı |

Aralık iki ucu da kapsar ve **asıl kaynak dosyasındaki sıraya** göre belirlenir; alfabetik sıra veya tablodaki güncel satır sırası kullanılmaz. En fazla 200 anahtar olabilir. Seslendirme metninde anahtar, senaryodaki `file` kimliğidir; `.wav` veya `.flac` eklenmez.

Her görevde tek dil ve tek arayüz tablosu ya da seslendirme rolü olsun. Kısa bir kapsamı incelemek kolaydır; oyun metni değiştiğinde daha az çakışma çıkar.

## 2. Çeviriye başlamadan kapsamı ayırın

Proje sorumlusu issue'ya şu yorumu yazar:

```text
/work assign
```

Botun ayırma işlemini onaylamasını bekle. Issue doldurmak veya kapatmak ya da tabloya isim yazmak görev ayırmaz veya serbest bırakmaz.

Bot görevi `community-work-state` dalındaki `registry.json` dosyasına kaydeder; issue alanlarını, tam kaynak anahtarlarını ve kaynak hash'ini sabitler. Aynı tür, dil ve tablo veya rol için başka bir etkin görevle çakışmayı reddeder. Farklı diller aynı kaynak anahtarlarında çalışabilir.

Issue metnini sonradan değiştirmek etkin görevi değiştirmez. Kapsam, çalışma dosyası, katkıcı veya inceleyici değişecekse proje sorumlusundan görevi serbest bırakıp doğru bilgilerle yeniden ayırmasını iste.

## 3. Tabloda çalışın

Proje sorumlusu güncel kaynak satırlarını sağlar ve atanan kişilere düzenleme izni verir. Bot dosyayı Google hesabına giriş yapmadan okuyabilmelidir; düzenleme izni ise yalnızca o işte çalışan kişilerle sınırlı tutulmalıdır. Kaynak anahtarları ve İngilizceyi korumaya al; katkıcılara yalnızca gerekli giriş hücrelerini aç. Bağlantısı olan herkesin düzenlemesine izin verme. Google izinleri ve korunan aralıklar elle ayarlanır; GitHub botu bunları yönetmez.

Arayüz çevirisi şu dört sütunu korur:

```text
key,en,translation,status
```

Sekmede yalnızca görevde belirtilen tek arayüz tablosunun satırları bulunmalıdır. Birkaç tabloyu birleştiren ana liste, başvuru kaynağıdır; doğrudan içe aktarılacak görev sekmesi değildir. Bot seçilen sekmedeki dolu satırların tamamını ilgili kaynak tabloyla karşılaştırır.

`translation` alanını düzenle ve mevcut `status` değerlerini kullan. Bir arayüz satırı ancak `status` boşsa aktarılabilir. `review` veya `outdated` aktarımı bekletir. Boş durum onay anlamına gelmez; ayrı inceleme adımı gerekir.

Yazılı seslendirme çevirileri için başlıklar ve sıraları tam olarak şöyle olmalıdır:

```text
Take file,English source,Translation,Review status,Notes,Role,Situation,Tone,Current voices,Source readiness,Source file,Source record
```

Mevcut Japonca, Rusça ve Korece sekmeleri bu yapıyı kullanır. Bot önce `Role` değerinin tam eşleşmesine göre, örneğin `carrier_jet_pilot`, filtreler; sonra ayrılan `Take file` anahtarlarını seçer. `Translation` alanını doldur ve metni incelenen satırların `Review status` değerini `Approved` yap.

Onaylanan metin `voice/translations/<locale>/<role>.csv` dosyasına `key,en,translation,status` biçiminde yazılır. Bu işlem yalnızca yazılı replikleri aktarır; ses kaydını onaylamaz veya taslak repliğin oyunda çalıştığını göstermez.

Her iki görev türünde de:

- Yer tutucuları, zorunlu etiketleri ve satır sonu belirteçlerini koru.
- Kaynak anahtarı ve İngilizce metni atanan kaynakla birebir aynı bırak.
- Önizlemeden önce ayrılan aralıktaki tüm çevirileri doldur.
- Hücreleri metin olarak kullan; çeviri getirmek veya oluşturmak için formül kullanma.
- Özel iletişim bilgilerini, ticket mesajlarını ve seçme kayıtlarını görev dosyasına veya issue'ya koyma.

Görev bitirilemeyecek kadar büyükse, yarım işi süresiz ayırmak yerine proje sorumlusuyla bölmeyi veya serbest bırakmayı görüş.

## 4. Önizleme isteyin ve inceleyin

Atanan katkıcı, atanan inceleyici veya bir proje sorumlusu şu yorumu yazar:

```text
/work preview
```

Bot ayrılan kapsamı herkese açık Google E-Tablolar CSV dışa aktarımından okur. Sabitlenen kaynağı, durumları, boş olmayan çevirileri ve gerekli değişkenleri kontrol eder. Daha sonraki onayda başkasının değişikliklerini fark edebilmek için depodaki mevcut çeviriyi de kontrol eder.

Değiştirilemez bir kopya kaydeder, inceleme bağlantısını ve SHA-256 özet değerini paylaşır. İnceleyici yalnızca issue özetini veya canlı tabloyu değil, **bu kopyayı** okumalıdır. Tablo önizlemeden sonra değişebilir. İngilizceye göre anlam ve bağlamı, doğal anlatımı ve sözlüğü, arayüz uzunluğunu veya söylenişi, yer tutucuları, etiketleri ve satır sonlarını kontrol et.

Düzeltme gerekiyorsa tabloyu düzenleyip `/work preview` komutunu yeniden çalıştır. Yeni özet değerini kullan. Önizleme bağlantısı inceleme içindir; PR birleştirme izni değildir.

## 5. Tam olarak incelenen kopyayı onaylayın

Yalnızca atanan inceleyici, örnek yerine önizlemedeki 64 karakterlik tam özet değerini yazar:

```text
/work approve <sha256>
```

Botun önizleme yanıtında `Digest:` etiketinden sonraki 64 karakterin tamamını kopyala ve komuttaki yalnızca `<sha256>` bölümünü bunlarla değiştir. Komutu çevirme ve örnekteki yer tutucuyu olduğu gibi gönderme.

Bot inceleyiciyi doğrular, tabloyu yeniden okur ve onaylanan kopyayla eşleşmesini şart koşar. Kaynağın ve depodaki hedef içeriğin de önizlemeden sonra değişmediğini kontrol eder. Tablo veya hedef dosya değişirse yeni önizleme gerekir. Asıl kaynak tablonun değişmesi ise aşağıda açıklandığı gibi yeni bir görev gerektirir.

Başarılı olursa doğrulanan dosyalarla PR açar; **PR'ı birleştirmez**. Tablodaki `Approved` değeri veya sıradan bir olumlu yorum bu komutun yerine geçmez. Proje sorumlusu farkları inceleyip kontroller geçtikten sonra birleştirene kadar iş ayrılmış kalır. Önerilen dosyalarla ilgili görüşmeleri PR içinde sürdür.

Güvenilir `reviewed-sheet` kuralı, PR'ı kayıtlı görev ve onaylı kopyayla karşılaştırır. PR dosyalarını veri olarak okur ve varsayılan daldaki güvenilir kodu çalıştırır. Elle açılmış çeviri PR'ını, değiştirilmiş teslim dosyasını veya teslimata eklenmiş fazladan dosyaları reddeder. Onaydan sonra bot dalını değiştirmek, incelenen metni başka metinle değiştirmeye izin vermez.

## 6. Görevi tamamlayın veya serbest bırakın

PR birleştirildiğinde veya kapatıldığında bir proje sorumlusu çalıştırır:

```text
/work sync
```

Birleştirilmiş PR görevi tamamlar; birleştirilmeden kapatılmış PR görevi serbest bırakır. Issue durumuna bakarak varsayma, botun onayını kontrol et. GitHub kayıtlı bir bot PR'ı için kapanış olayı gönderdiğinde koordinatör de durumu eşitler. Bu otomatik çalışma tamamlanmazsa komutu elle kullan. Açık bir PR için `/work sync` kontrolleri yeniden ister; PR oluşturulurken kontrol başlatma başarısız olmuşsa kullanabilirsin.

Henüz PR yokken görevi iptal etmek için proje sorumlusu yorum yapar:

```text
/work release
```

Serbest bırakmadan önce açık PR kapatılmalıdır. Böylece aynı aralığa iki etkin teslim yapılamaz.

| Komut | Kim kullanabilir? | Sonuç |
| --- | --- | --- |
| `/work assign` | Proje sorumlusu | Görev bilgilerini sabitler ve aralığı ayırır. |
| `/work preview` | Atanan katkıcı, atanan inceleyici veya proje sorumlusu | İncelenecek kopyayı doğrular ve kaydeder. |
| `/work approve <sha256>` | Atanan inceleyici | Tam kopyayı tekrar kontrol eder ve PR açar. |
| `/work release` | Proje sorumlusu | Açık PR yoksa ayırmayı iptal eder. |
| `/work sync` | Proje sorumlusu | PR durumunu kayıtla eşitler. |

## Oyun metni değiştiğinde

Her oyun sürümü için yeni çalışma dosyası oluşturma. Sabit kaynak kimlikleri çevirilerin korunmasını sağlar. Yeni satırları deponun kaynak güncelleme sürecinden ekle ve değişen çevirileri [Yerelleştirme](../../localization/README.md) kılavuzuna göre incelemeye işaretle.

Görev, **arayüz tablosunun veya seslendirme rolünün tamamının** sabit bir kaynak kopyasını kullanır. Onaydan önce bu asıl tablo değişirse, ayrılan anahtarlar değişmemiş olsa bile bot aktarımı durdurur. Proje sorumlusu varsa açık teslim PR'ını kapatır, eski görevi serbest bırakır, tablodaki kaynak satırlarını günceller ve **yeni bir görev issue'su** açar. Gönüllünün çevirisini silme; yeni kaynakla karşılaştırarak koru. İnceleyici yeni önizlemeyi inceler. Başka kaynak tablolardaki görevler devam edebilir.

Gerçek kaynak kimliği olmayan planlama satırı aktarıma hazır değildir. Geliştirici asıl kaynak girdisini ekleyene kadar planlamada tut. Üretim kimliği uydurma veya gelecekteki içeriği eklemek için tüm tabloyu yükleme.

## Proje sorumluları için kurulum ve sınırlar

- İş akışını ancak kodu ve issue formu varsayılan dala birleştirildikten sonra aç. Etkin komutlar çalışırken `community-work-state` kaydını elle değiştirme.
- Akış; durum ve bot dalını yazma, issue'lara yorum yapma ve PR açma izinleriyle deponun `GITHUB_TOKEN` değerini kullanır. Google OAuth bağlantısı veya kişisel erişim token'ı gerekmez. Google erişimi yalnızca herkese açık CSV okumaktır.
- Actions ayarlarından GitHub Actions'ın PR oluşturmasına izin ver. Bot kimliği ile insan inceleyicinin hesabını ayrı tut.
- Bot PR'ının normal `pull_request` iş akışlarını başlatacağına güvenme. İçe aktarıcı önce aday dosyaları doğrular; sonra bot dalı için `check.yml` ve ilgili PR numarası için güvenilir varsayılan daldan `delivery-policy.yml` akışını açıkça başlatır.
- Varsayılan dalda iki zorunlu kontrolü kullan: `check` ve `reviewed-sheet` commit durumu. Kural akışı bu durumu yayımlayabilmelidir. Birleştirmeden önce ikisinin de başarılı olduğunu doğrula. Akış dosyalarını oluşturmak, dal koruma ayarlarını tek başına etkinleştirmez.
- Kayıt çakışan görevleri önler; zorunlu teslim kuralı elle açılan çeviri PR'larının bunu atlamasını engeller. İkisi de Google düzenleme izinlerini yönetmez: düzenlemeyi sınırla ve kaynak sütunlarını koru.

Otomatik kontroller yapısal hataları ve güncelliğini yitirmiş içeriği yakalar. Çeviri kalitesi, bağlam, katkı şartları ve oyuna uygunluk insan incelemesinin sorumluluğundadır.
