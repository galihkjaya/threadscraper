KEYWORDS = [
    # Politik
    "politik indonesia", "pilkada", "pemilu indonesia", "korupsi pejabat",
    "prabowo presiden", "jokowi dikritik", "gibran kontroversial",
    "anies baswedan", "mahkamah konstitusi", "dprd viral",
    "kebijakan pemerintah", "partai politik indonesia", "oposisi indonesia",
    "demo mahasiswa indonesia", "aktivis ditangkap", "uu kontroversial",
    "tapera kontroversial", "buzzer politik", "hoaks politik",

    # Ekonomi
    "ekonomi indonesia", "bbm naik", "harga beras mahal",
    "phk massal", "upah minimum", "ojol demo",
    "pinjol ilegal", "investasi bodong", "startup tutup indonesia",
    "umkm vs marketplace", "tiktok shop pedagang", "kripto indonesia",
    "pengangguran indonesia", "daya beli turun", "inflasi indonesia",

    # Agama
    "agama indonesia kontroversial", "fatwa mui", "intoleransi agama",
    "ceramah viral kontroversial", "ormas membubarkan", "penistaan agama",
    "pesantren kekerasan", "nikah beda agama", "khilafah pancasila",
    "ulama politik indonesia", "aliran sesat", "toleransi beragama",

    # Sosial
    "feminisme indonesia", "lgbt indonesia", "childfree indonesia",
    "nikah muda indonesia", "kdrt viral", "body shaming indonesia",
    "cancel culture indonesia", "diskriminasi ras indonesia",
    "rasisme papua", "konflik sosial viral", "netizen menghakimi",
    "cyberbullying indonesia", "victim blaming", "standar ganda",

    # Pendidikan
    "ukt mahal", "mahasiswa demo rektor", "skripsi dihapus",
    "ppdb zonasi masalah", "guru kekerasan", "bullying sekolah viral",
    "kurikulum merdeka kontroversi", "kampus bermasalah",
    "dosen pelecehan", "ijazah palsu", "beasiswa tidak merata",

    # Hiburan
    "artis skandal indonesia", "youtuber kontroversial",
    "selebgram bermasalah", "podcast kontroversial indonesia",
    "idol kpop haram", "film indonesia kontroversial",
    "konser dibatalkan", "plagiat lagu indonesia",
    "sinetron tidak mendidik", "endorse judi online artis",

    # Hukum
    "vonis ringan koruptor", "polisi viral kekerasan",
    "uu ite menjerat", "hakim suap", "kpk melemah",
    "salah tangkap polisi", "hukuman mati indonesia",
    "mafia peradilan", "napi kabur", "koruptor fasilitas mewah",

    # Lingkungan
    "tambang merusak lingkungan", "deforestasi kalimantan",
    "polusi udara jakarta", "kebakaran hutan indonesia",
    "reklamasi pantai kontroversi", "banjir rob semarang",
    "proyek merusak amdal", "sampah plastik indonesia",
    "illegal fishing", "satwa dilindungi diperjualbelikan",

    # Kesehatan
    "bpjs bermasalah", "dokter malpraktik viral",
    "antivaksin indonesia", "hoaks kesehatan viral",
    "stunting indonesia gagal", "mental health indonesia",
    "obat langka mahal", "rs menolak pasien",
    "narkoba indonesia", "rokok iklan anak",

    # Teknologi
    "tiktok diblokir indonesia", "data bocor indonesia",
    "judi online merajalela", "pdns jebol",
    "ai ancam pekerjaan indonesia", "deepfake indonesia",
    "penipuan online modus baru", "kominfo blokir",
    "starlink vs telkom", "fintech predatory indonesia",
]

TARGET_COMMENTS = 10_000

DELAY_MIN = 2.0
DELAY_MAX = 5.0
OUTPUT_FILE = "dataset.csv"
CHECKPOINT_FILE = "checkpoint.json"
MIN_TEXT_LENGTH = 10       # Minimal karakter per komentar
MIN_REPLY_COUNT = 5        # Hanya scrape post yang punya minimal N replies

BASE_HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.5",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://www.threads.com",
    "referer": "https://www.threads.com/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/148.0.0.0 Safari/537.36"
    ),
    "x-asbd-id": "359341",
    "x-bloks-version-id": "958ddf5567bf796d407cf4fa808fa2f3f8076fd15416ddf33b48a5ad65ae7a39",
    "x-fb-friendly-name": "BarcelonaPostPageDirectQuery",
    "x-ig-app-id": "238260118697367",
    "x-logged-out-threads-migrated-request": "true",
    "x-root-field-name": "xdt_api__v1__text_feed__media_id__replies__connection",
}

BASE_PAYLOAD = {
    "av": "0",
    "__user": "0",
    "__a": "1",
    "dpr": "1",
    "__ccg": "EXCELLENT",
    "__rev": "1039758770",
    "__hsi": "7641430579493761939",
    "__comet_req": "122",
    "hl": "en",
    "lsd": "AdTbHLdt2iCABzoyWTVcPeCzSpc",
    "jazoest": "22438",
    "__spin_r": "1039758770",
    "__spin_b": "trunk",
    "__spin_t": "1779159200",
    "fb_api_caller_class": "RelayModern",
    "fb_api_req_friendly_name": "BarcelonaPostPageDirectQuery",
    "server_timestamps": "true",
    "doc_id": "26739870295663957",
}

COOKIES = {
    "csrftoken": "PynEgJcSw_b1pZyWHRwQMi",
    "ig_did": "698661E1-FD19-425F-AE49-B37B79139E90",
    "mid": "agvQSQALAAHJl86pSrbYoX1LDWjI",
}