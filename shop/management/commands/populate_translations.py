from django.core.management.base import BaseCommand
from django.db import connection

from shop.models import Banner, Category, City, Product

CATEGORY_TRANSLATIONS = {
    'Ерлер':    ('Men',      'Мужское'),
    'Әйелдер':  ('Women',    'Женское'),
    'Балалар':  ('Children', 'Детское'),
}

CITY_TRANSLATIONS = {
    'Астана':   ('Astana',   'Астана'),
    'Алматы':   ('Almaty',   'Алматы'),
    'Шымкент':  ('Shymkent', 'Шымкент'),
    'Семей':    ('Semey',    'Семей'),
}

PRODUCT_TRANSLATIONS = {
    'Balloon джинсы': (
        'Balloon Jeans',
        'Джинсы Balloon',
        '- Balloon fit silhouette\n- 100% cotton denim\n- Wide silhouette, tapered at the hem\n- Mid-rise waist',
        '- Силуэт Balloon fit\n- 100% хлопковый деним\n- Широкий силуэт, зауженный к низу\n- Пояс на уровне бёдер',
    ),
    'Bow кең джинсы': (
        'Bow Wide-Leg Jeans',
        'Широкие джинсы Bow',
        '- Relaxed fit\n- Mid-rise waist\n- 100% cotton\n- Active wash effects\n- Classic 5-pocket design',
        '- Свободный крой\n- Средняя посадка\n- 100% хлопок\n- С эффектами активной стирки\n- Классический 5-карманный дизайн',
    ),
    'Straight түзу джинсы': (
        'Straight-Cut Jeans',
        'Прямые джинсы',
        '- Straight fit silhouette\n- 100% cotton raw denim (saturated, dense)\n- Classic 5-pocket design\n- Button fly',
        '- Силуэт Straight fit\n- 100% хлопковый сырой деним (насыщенный, плотный)\n- Классический 5-карманный дизайн\n- Пуговичная застёжка',
    ),
    'V тәрізді мойын ойындысы бар текстуралық жемпір': (
        'Textured Sweater with V-Neck',
        'Текстурный свитер с V-образным вырезом',
        '- Comfort Fit silhouette\n- 100% cotton\n- Textured cotton yarn\n- Slightly oversized',
        '- Силуэт Comfort Fit\n- 100% хлопок\n- Текстурная хлопковая нить\n- Слегка свободный крой',
    ),
    'Джинс жейде-куртка': (
        'Denim Shirt-Jacket',
        'Джинсовая рубашка-куртка',
        '- Relaxed fit silhouette\n- Raw denim (saturated, dense)\n- Long sleeves\n- Turned-down collar\n- 2 patch pockets',
        '- Силуэт Relaxed fit\n- Сырой деним (насыщенный, плотный)\n- Длинные рукава\n- Отложной воротник\n- 2 накладных кармана',
    ),
    'Жазуы бар бейсболка': (
        'Baseball Cap with Text',
        'Бейсболка с надписью',
        'Baseball cap with text print\nCountry of origin: China\nMaterial: 100% cotton',
        'Бейсболка с надписью\nСтрана производства: Китай\nСостав: 100% хлопок',
    ),
    'Жасанды былғарыдан тігілген бомбер': (
        'Faux Leather Bomber',
        'Бомбер из искусственной кожи',
        '- Oversized fit\n- Ribbed waistband and cuffs\n- Long sleeves\n- Central metal zipper',
        '- Свободный крой\n- Трикотажные пояс и манжеты\n- Длинные рукава\n- Центральная металлическая молния',
    ),
    'Жасанды күдері бомбер': (
        'Faux Suede Bomber',
        'Бомбер из искусственной замши',
        '- Oversized fit\n- Ribbed waistband and cuffs\n- Long sleeves\n- Central metal zipper',
        '- Свободный крой\n- Трикотажные пояс и манжеты\n- Длинные рукава\n- Центральная металлическая молния',
    ),
    'Бомбер': (
        'Bomber',
        'Бомбер',
        'Country of origin: China\nMaterial: outer: 100% polyester; lining: 100% polyester',
        'Страна производства: Китай\nСостав: основная ткань: 100% полиэстер; подкладка: 100% полиэстер',
    ),
    'Бүкпелері бар түзу шалбар': (
        'Straight Pants with Pleats',
        'Прямые брюки со складками',
        '- Mid-rise waist\n- Zip with hook and eye closure\n- 2 side pockets\n- 2 back welt pockets',
        '- Средняя посадка\n- Молния с крючком и петлёй\n- 2 боковых кармана\n- 2 задних кармана',
    ),
    'Жасанды былғарыдан тігілген жеңіл куртка': (
        'Lightweight Faux Leather Jacket',
        'Лёгкая куртка из искусственной кожи',
        'Country of origin: China\nMaterial: outer: faux leather (coating: 100% polyurethane, base: 100% polyester); lining: 100% polyester',
        'Страна производства: Китай\nСостав: верх: искусственная кожа (покрытие 100% полиуретан, основа 100% полиэстер); подкладка: 100% полиэстер',
    ),
    'Жасанды былғарыдан тігілген куртка': (
        'Faux Leather Jacket',
        'Куртка из искусственной кожи',
        'Country of origin: China\nMaterial: outer: faux leather (coating: 100% polyurethane, base: 100% polyester); lining: 100% polyester',
        'Страна производства: Китай\nСостав: верх: искусственная кожа (покрытие 100% полиуретан, основа 100% полиэстер); подкладка: 100% полиэстер',
    ),
    'Жасанды былғарыдан тігілген қысқа пальто': (
        'Short Faux Leather Coat',
        'Короткое пальто из искусственной кожи',
        'Country of origin: China\nMaterial: outer: faux leather (coating: 100% polyurethane, base: 100% viscose); lining: 100% polyester',
        'Страна производства: Китай\nСостав: верх: искусственная кожа (покрытие 100% полиуретан, основа 100% вискоза); подкладка: 100% полиэстер',
    ),
    'Жасанды күдеріден тігілген Baggy шалбары': (
        'Faux Suede Baggy Pants',
        'Широкие брюки из искусственной замши',
        '- Baggy fit\n- Elastic drawstring waist\n- 2 side pockets\nCountry of origin: China',
        '- Силуэт Baggy\n- Эластичный пояс на кулиске\n- 2 боковых кармана\nСтрана производства: Китай',
    ),
    'Жасанды күдеріден тігілген куртка': (
        'Faux Suede Jacket',
        'Куртка из искусственной замши',
        'Country of origin: China\nMaterial: outer: 92% polyester, 8% elastane; lining: 100% polyester',
        'Страна производства: Китай\nСостав: основная ткань: 92% полиэстер, 8% эластан; подкладка: 100% полиэстер',
    ),
    'Қыздар легинсі': (
        "Girls' Leggings",
        'Леггинсы для девочек',
        '- Ribbed knit fabric\n- Leggings style\n- Full length\n- Close-fitting silhouette\n- Elastic waistband',
        '- Трикотаж в рубчик\n- Модель лосины\n- Полная длина\n- Облегающий силуэт\n- Резинка на поясе',
    ),
    'Қыздар шалбары': (
        "Girls' Pants",
        'Брюки для девочек',
        '- Suit twill fabric\n- Solid colour design\n- Wide fit\n- Straight silhouette\n- Full length\n- Side pockets',
        '- Костюмный твил\n- Однотонный дизайн\n- Широкий крой\n- Прямой силуэт\n- Полная длина\n- Боковые карманы',
    ),
    'Қыздарға арналған джинс жейде': (
        "Girls' Denim Shirt",
        'Джинсовая рубашка для девочек',
        '- Solid colour denim\n- Wide fit\n- Long sleeves\n- Button front closure',
        '- Однотонный деним\n- Широкий крой\n- Длинные рукава\n- Застёжка на пуговицы',
    ),
    'Қыздарға арналған жылы кеудеше': (
        "Girls' Warm Vest",
        'Тёплый жилет для девочек',
        '- Matte fabric\n- Pongee lining\n- Solid colour\n- Wide fit\n- Synthetic down insulation',
        '- Матовая ткань\n- Подкладка из понже\n- Однотонный\n- Широкий крой\n- Утеплитель — синтетический пух',
    ),
    'Қыздарға арналған жылы куртка': (
        "Girls' Warm Jacket",
        'Тёплая куртка для девочек',
        '- Water-repellent and waterproof fabric\n- Synthetic down insulation\n- Short length\n- Straight silhouette',
        '- Водоотталкивающая и водостойкая ткань\n- Утеплитель — синтетический пух\n- Короткая длина\n- Прямой силуэт',
    ),
    'Қыздарға арналған карго-қалталы шалбар': (
        "Girls' Cargo Pants",
        'Карго-брюки для девочек',
        '- Relaxed fit\n- Suit fabric\n- Solid colour design\n- Wide fit\n- Full length',
        '- Свободный крой\n- Костюмная ткань\n- Однотонный дизайн\n- Широкий крой\n- Полная длина',
    ),
    'Қыздарға арналған кардиган': (
        "Girls' Cardigan",
        'Кардиган для девочек',
        '- Thin knit fabric\n- Solid colour knit\n- Semi-fitted\n- Straight silhouette\n- Hip length',
        '- Тонкий трикотаж\n- Однотонное вязание\n- Полуприлегающий крой\n- Прямой силуэт\n- Длина до бедра',
    ),
    'Қыздарға арналған кең балақты трикотаж шалбар': (
        "Girls' Wide-Leg Knit Pants",
        'Широкие трикотажные брюки для девочек',
        '- Smooth fleece knit fabric\n- Solid colour\n- Wide fit\n- Straight silhouette',
        '- Гладкий футер без ворса\n- Однотонный\n- Широкий крой\n- Прямой силуэт',
    ),
}


class Command(BaseCommand):
    help = 'Populate English and Russian translations for all DB content'

    def handle(self, *args, **options):
        self._populate_categories()
        self._populate_cities()
        self._populate_products()
        self.stdout.write(self.style.SUCCESS('All translations populated successfully.'))

    def _raw(self, sql):
        with connection.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()

    def _populate_categories(self):
        rows = self._raw("SELECT id, name FROM shop_category")
        count = 0
        for pk, kk_name in rows:
            en, ru = CATEGORY_TRANSLATIONS.get(kk_name, (None, None))
            if en:
                Category.objects.filter(pk=pk).update(name_kk=kk_name, name_en=en, name_ru=ru)
                count += 1
        self.stdout.write(f'  Categories: {count} updated')

    def _populate_cities(self):
        rows = self._raw("SELECT id, name FROM shop_city")
        count = 0
        for pk, kk_name in rows:
            en, ru = CITY_TRANSLATIONS.get(kk_name, (None, None))
            if en:
                City.objects.filter(pk=pk).update(name_kk=kk_name, name_en=en, name_ru=ru)
                count += 1
        self.stdout.write(f'  Cities: {count} updated')

    def _populate_products(self):
        rows = self._raw("SELECT id, name, description FROM shop_product")
        count = 0
        skipped = []
        for pk, kk_name, kk_desc in rows:
            if kk_name in PRODUCT_TRANSLATIONS:
                en_name, ru_name, en_desc, ru_desc = PRODUCT_TRANSLATIONS[kk_name]
                Product.objects.filter(pk=pk).update(
                    name_kk=kk_name, name_en=en_name, name_ru=ru_name,
                    description_kk=kk_desc, description_en=en_desc, description_ru=ru_desc,
                )
                count += 1
            else:
                skipped.append(kk_name)
        self.stdout.write(f'  Products: {count} updated')
        if skipped:
            self.stdout.write(self.style.WARNING(f'  Skipped (no translation): {skipped}'))
