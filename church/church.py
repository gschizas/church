# -*- coding: utf-8 -*-
"""
:copyright: (c) 2016 by Likid Geimfari <likid.geimfari@gmail.com>.
:software_license: MIT, see LICENSES for more details.
:repository: https://github.com/lk-geimfari/church
"""
import array
from datetime import (
    date, timedelta,
    datetime
)
from hashlib import (
    sha1, sha256,
    sha512, md5
)
from itertools import product
from random import (
    choice, sample,
    randint, uniform,
    random
)
from string import (
    digits, ascii_letters,
    ascii_uppercase
)

import church._common as common
from .utils import pull, PATH

__all__ = ['Address', 'Personal',
           'Text', 'Network',
           'Datetime', 'File',
           'Science', 'Development',
           'Food', 'Hardware',
           'Numbers', 'Business',
           'Church'
           ]


class Church(object):
    """
    A lazy initialization of locale for all classes that have locales.
    """

    def __init__(self, locale):
        """
        :param locale: Locale code.
        """
        self.locale = locale
        self._personal = Personal
        self._address = Address
        self._datetime = Datetime
        self._business = Business
        self._text = Text
        self._food = Food
        self._science = Science
        self.file = File()
        self.numbers = Numbers()
        self.development = Development()
        self.hardware = Hardware()
        self.network = Network()

    # TODO: Rewrite all @property as a dynamic.
    @property
    def personal(self):
        if callable(self._personal):
            self._personal = self._personal(self.locale)
        return self._personal

    @property
    def address(self):
        if callable(self._address):
            self._address = self._address(self.locale)
        return self._address

    @property
    def datetime(self):
        if callable(self._datetime):
            self._datetime = self._datetime(self.locale)
        return self._datetime

    @property
    def business(self):
        if callable(self._business):
            self._business = self._business(self.locale)
        return self._business

    @property
    def text(self):
        if callable(self._text):
            self._text = self._text(self.locale)
        return self._text

    @property
    def food(self):
        if callable(self._food):
            self._food = self._food(self.locale)
        return self._food

    @property
    def science(self):
        if callable(self._science):
            self._science = self._science(self.locale)
        return self._science


class Address(object):
    """
    Class for generate fake address data.
    """

    def __init__(self, locale='en'):
        """
        :param locale: Current language.
        """
        self.locale = locale
        self.data = pull('address.json', self.locale)

    @staticmethod
    def street_number(maximum=1400):
        """
        Generate a random street number.

        :returns: Street number.
        :Example:
            134.
        """

        number = randint(1, int(maximum))
        return '{}'.format(number)

    def street_name(self):
        """
        Get a random street name.

        :returns: Street name.
        :Example:
           Candlewood.
        """
        names = self.data['street']['name']
        return choice(names)

    def street_suffix(self):
        """
        Get a random street suffix.

        :returns: Street suffix.
        :Example:
            Street.
        """
        suffixes = self.data['street']['suffix']
        return choice(suffixes)

    def address(self):
        """
        Get a random full address.

        :returns: Full address (include Street number, suffix and name).
        :Example:
            5 Central Sideline.
        """
        ru = '{2} {1} {0}'  # Russian address format
        fr = '{0} {2} {1}'  # French address format
        intl = '{} {} {}'  # international format

        def _f():
            if self.locale in ('sv', 'de', 'fi', 'nl', 'is'):
                return '{} {}'.format(
                    self.street_name(),
                    self.street_number()
                )

            # specific format for some locales
            fmt = ru if self.locale == 'ru' else \
                fr if self.locale == 'fr' else intl

            return fmt.format(
                self.street_number(),
                self.street_name(),
                self.street_suffix()
            )

        return _f()

    def state(self, iso_code=False):
        """
        Get a random states or subject of country.

        :param iso_code: If True then return ISO (ISO 3166-2)
        code of state/region/province/subject.
        :returns: State of current country.
        :Example:
            Alabama (for locale `en`).
        """
        key = 'iso_code' if iso_code else 'name'
        states = self.data['state'][key]
        return choice(states)

    def postal_code(self):
        """
        Get a random postal code.

        :returns: postal code.
        :Example:
            389213
        """
        _ = Personal.identifier

        codes = {
            'ru': _(mask='######'),
            'nl': _(mask='####', suffix=True),
            'is': _(mask='###'),
            'pt': _(mask='####'),
            'no': _(mask='####'),
            'da': 'DK-' + _(mask='####'),
            'br-pt': _(mask='#####-###'),
            'default': _(mask='#####')
        }
        if self.locale in codes:
            return codes[self.locale]

        return codes['default']

    def country(self, iso_code=False):
        """
        Get a random country.

        :param iso_code: Return only ISO code of country.
        :returns: The Country
        :Example:
            Russia.
        """
        if iso_code:
            return choice(common.COUNTRY_ISO_CODE)

        countries = self.data['country']['name']
        return choice(countries)

    def city(self):
        """
        Get a random name of city.

        :returns: City name.
        :Example:
            Saint Petersburg.
        """
        cities = self.data['city']
        return choice(cities)

    @staticmethod
    def latitude():
        """
        Generate a random value of latitude (-90 to +90)

        :returns: Value of longitude.
        :Example:
            -66.4214188124611
        """
        return uniform(-90, 90)

    @staticmethod
    def longitude():
        """
        Generate a random value of longitude (-180 to +180).

        :returns: Value of longitude.
        :Example:
            112.18440260511943
        """
        return uniform(-180, 180)

    def coordinates(self):
        """
        Generate random geo coordinates.

        :returns: Dict with coordinates.
        :Example:
            {'latitude': 8.003968712834975,
            'longitude': 36.02811153405548
            }
        """
        coord = {
            'longitude': self.longitude(),
            'latitude': self.latitude()
        }
        return coord


class Numbers(object):
    """
    Class for generating numbers.
    """

    @staticmethod
    def floats(n=2, type_code='f', to_list=False):
        """
        Generate an array of random float number of 10**n

        +-----------+----------------+--------------+----------------------+
        | Type Code | C Type         | Storage size | Value range          |
        +===========+================+==============+======================+
        | 'f'       | floating point | 4 byte       | 1.2E-38 to 3.4E+38   |
        +-----------+----------------+--------------+----------------------+
        | 'd'       | floating point | 8 byte       | 2.3E-308 to 1.7E+308 |
        +-----------+----------------+--------------+----------------------+

        :param n: Raise 10 to the 'n' power.
        :param type_code: A code of type.
        :param to_list: Convert array to list.

        .. note:: When you work with large numbers, it is better not to use
            this option, because type 'array' much faster than 'list'.

        :returns: An array of floating-point numbers.
        """
        nums = array.array(type_code, (random() for _ in range(10 ** int(n))))
        nums = nums.tolist() if to_list else nums
        return nums

    @staticmethod
    def primes(n=2, to_list=False):
        """
        Generate an array of prime numbers of 10 ** n

        +------------+-----------------+--------------+--------------------+
        | Type Code | C Type           | Storage size | Value range        |
        +===========+==================+==============+====================+
        | 'L'       | unsigned integer | 4 byte       | 0 to 4,294,967,295 |
        +-----------+------------------+--------------+--------------------+

        :param to_list: Convert array to list.
        :returns: An array of floating-point numbers.
        """
        nums = array.array('L', (i for i in range(10 ** n) if i % 2))
        nums = nums.tolist() if to_list else nums
        return nums


class Text(object):
    """
    Class for generate text data, i.e text, lorem ipsum and another.
    """

    def __init__(self, locale='en'):
        """
        :param locale: Current language.
        """
        self.locale = locale
        self.data = pull('text.json', self.locale)

    def text(self, quantity=5):
        """
        Get random strings. Not only lorem ipsum.

        :param quantity: Quantity of sentences.
        :returns: Text.
        :Example:
            Haskell is a standardized, general-purpose purely
            functional programming language, with non-strict semantics
            and strong static typing.
        """
        text = ''
        for _ in range(quantity):
            text += ' ' + choice(self.data['text'])
        return text.strip()

    def sentence(self):
        """
        Get a random sentence from text.

        :returns: Sentence.
        :Example:
            Any element of a tuple can be accessed in constant time.
        """
        return self.text(quantity=1)

    def title(self):
        """
        Get a random title.

        :returns: The title.
        :Example:
            Erlang - is a general-purpose, concurrent,
            functional programming language.
        """
        return self.text(quantity=1)

    def words(self, quantity=5):
        """
        Get the random words.

        :param quantity: Quantity of words. Default is 5.
        :returns: Word list.
        :Example:
            science, network, god, octopus, love.
        """
        words_list = []
        words = self.data['words']['normal']
        for _ in range(int(quantity)):
            words_list.append(choice(words))
        return words_list

    def word(self):
        """
        Get a random word.

        :returns: Single word.
        :Example:
            Science.
        """
        return self.words(quantity=1)[0]

    def swear_word(self):
        """
        Get a random swear word.

        :returns: Swear word.
        :Example:
            Damn.
        """
        bad_words = self.data['words']['bad']
        return choice(bad_words)

    @staticmethod
    def naughty_strings():
        """
        Get a random naughty string form file.

        Authors of big-list-of-naughty-strings is Max Woolf and contributors.
        Thank you to all who have contributed in big-list-of-naughty-strings.
        Repository: https://github.com/minimaxir/big-list-of-naughty-strings

        :returns: The list of naughty strings.
        """
        import os.path as op

        with open(op.join(PATH + '/etc', 'naughty_strings'), 'r') as f:
            naughty_list = [x.strip(u'\n') for x in f.readlines()]

        return naughty_list

    def quote(self):
        """
        Get a random quotes from movie.

        :returns: Quote from movie.
        :Example:
            "Bond... James Bond."
        """
        quotes = self.data['quotes']
        return choice(quotes)

    def color(self):
        """
        Get a random name of color.

        :returns: Color name.
        :Example:
            Red.
        """
        colors = self.data['color']
        return choice(colors)

    @staticmethod
    def hex_color():
        """
        Generate a hex color.

        :returns: Hex color code.
        :Example:
            #D8346B
        """
        letters = '0123456789ABCDEF'
        color_code = '#' + ''.join(sample(letters, 6))
        return color_code

    @staticmethod
    def emoji():
        """
        Get a random EMOJI shortcut code.

        :returns: Emoji code.
        :Example:
            :kissing:
        """
        return choice(common.EMOJI)

    @staticmethod
    def image_placeholder(width='400', height='300'):
        url = 'http://placehold.it/{0}x{1}'.format(width, height)
        return url

    @staticmethod
    def hashtags(quantity=4, category='general'):
        """
        Create a list of hashtags (for Instagram, Twitter etc.)

        :param quantity: The quantity of hashtags.
        :param category: The category of hashtag.

        Available categories:
          1. general - #nice, #day, #tree etc.
          2. girls - #lady, #beautiful, #girlsday etc.
          3. boys - #men, #guys, #dude etc.
          4. love - #love, #romantic, #relationship etc.
          5. friends - #crazy, #party etc.
          6. family - #fam, #sister, #brother etc.
          7. nature - #nature, #tree, #blue, #sky etc.
          8. travel - #natureaddict, #sunset etc.
          9. cars - #car, #ride, #drive etc.
          10. sport - #soccer, #game etc.
          11. tumblr - #perfect, #tumblr etc.

        :returns: The list of hashtags.
        :Example:
            ['#love', '#sky', '#nice']
        """
        k = category.lower()
        tags = [choice(common.HASHTAGS[k]) for _ in range(int(quantity))]
        return tags

    @staticmethod
    def weather(scale='c', minimum=-30, maximum=40):
        """
        Generate a random temperature value.

        :param scale: Scale of temperature.
        :param minimum: Minimum value of temperature.
        :param maximum: Maximum value of temperature.
        :returns: Temperature in Celsius or Fahrenheit.
        :Example:
            33.4 °C.
        """
        n = randint(minimum, maximum)
        # Convert to Fahrenheit
        n = (n * 1.8) + 32 if scale.lower() == 'f' else n
        scale = '°C' if scale.lower() == 'c' else '°F'

        return '{0:0.1f} {1}'.format(n, scale)


class Business(object):
    """
    Class for generating data for business.
    """

    def __init__(self, locale='en'):
        self.locale = locale
        self.data = pull('business.json', self.locale)

    def company_type(self, abbr=False):
        """
        Get a random company type.

        :param abbr: if True then abbreviated company type.
        :returns: Company type.
        :Example:
            Incorporated (Inc. when abbr=True).
        """
        key = 'abbr' if abbr else 'title'
        company_type = self.data['company']['type'][key]
        return choice(company_type)

    def company(self):
        """
        Get a random company name.

        :returns: Company name.
        :Example:
            Gamma Systems
        """
        companies = self.data['company']['name']
        return choice(companies)

    def copyright(self, minimum=1990, maximum=2016, without_date=False):
        """
        Generate a random copyright.

        :param minimum: Foundation date
        :param maximum: Current date
        :param without_date: When True will be returned
            copyright without date.
        :returns: Copyright of company.
        :Example:
            © 1990-2016 Komercia, Inc.
        """
        founded = randint(int(minimum), int(maximum))
        company = self.company()
        ct = self.company_type(abbr=True)
        if not without_date:
            return '© {}-{} {}, {}'.format(founded, maximum, company, ct)
        return '© {}, {}'.format(company, ct)

    @staticmethod
    def currency_iso():
        """
        Get a currency code. ISO 4217 format.

        :returns: Currency code.
        :Example:
            RUR.
        """
        return choice(common.CURRENCY)


class Personal(object):
    """
    Class for generate personal data, i.e names, surnames, age and another.
    """

    def __init__(self, locale='en'):
        """
        :param locale: Current language.
        """
        self.locale = locale
        self.data = pull('personal.json', self.locale)

    @staticmethod
    def age(minimum=16, maximum=66):
        """
        Get a random integer value.

        :param maximum: max age
        :param minimum: min age
        :returns: Random integer (from minimum=16 to maximum=66)
        :Example:
            23.
        """
        return randint(minimum, maximum)

    def name(self, gender='female'):
        """
        Get a random name.

        :param gender: if 'male' then will getting male name else female name.
        :returns: Name.
        :Example:
            John Abbey (gender='male').
        """
        if not isinstance(gender, str):
            raise TypeError('name takes only string type')

        names = self.data['names'][gender]
        return choice(names)

    def surname(self, gender='female'):
        """
        Get a random surname.

        :param gender: The gender of person.
        :returns: Surname.
        :Example:
            Smith.
        """
        if not isinstance(gender, str):
            raise TypeError('surname takes only string type')

        # In Russian Federation and Iceland surnames
        # separated by gender.
        diff_surnames = ('ru', 'is')

        if self.locale in diff_surnames:
            return choice(self.data['surnames'][gender])

        return choice(self.data['surnames'])

    def title(self, gender='female', type_=None):
        """
        Get a random title (prefix/suffix) for name.

        :param gender: The gender.
        :param type_:  The type of title. Available types:
        +-------------------+-------------------------+
        | Key of type       |      An example (M/F)   |
        +===================+=========================+
        | typical           |      Mr./Mrs.           |
        +-------------------+-------------------------+
        | aristocratic      |      Prince/Princess    |
        +-------------------+-------------------------+
        | religious         |      Brother/Sister     |
        +-------------------+-------------------------+
        | academic          |      PhD, Dr.           |
        +-------------------+-------------------------+
        :return: The title.
        :Example:
            PhD.
        """
        if not type_:
            type_ = 'typical'

        titulus = self.data['title'][gender][type_]
        return titulus

    def full_name(self, gender='female', reverse=False):
        """
        Get a random full name.

        :param reverse: if true: surname/name else name/surname
        :param gender: if gender='male' then will be returned male name else
            female name.
        :returns: Full name.
        :Example:
            Johann Wolfgang.
        """
        sex = gender.lower()
        fmt = '{1} {0}' if reverse else '{0} {1}'
        fn = fmt.format(self.name(sex), self.surname(sex))
        return fn

    @staticmethod
    def username(gender='female'):
        """
        Get a random username with digits.
        Username generated from names (en) for all locales.

        :returns: Username.
        :Example:
            abby1189.
        """
        data = pull('personal.json', 'en')
        username = choice(data['names'][gender])
        return '{}{}'.format(username.lower(), randint(2, 9999))

    @staticmethod
    def twitter(gender='female'):
        """
        Get a random twitter user.

        :param gender: Gender of user.
        :returns: URL to user.
        :Example:
            http://twitter.com/some_user
        """
        url = "http://twitter.com/{0}"
        username = Personal.username(gender)
        return url.format(username)

    @staticmethod
    def facebook(gender='female'):
        """
        Generate a random facebook user.

        :param gender: Gender of user.
        :returns: URL to user.
        :Example:
            https://facebook.com/some_user
        """
        url = 'https://facebook.com/{0}'
        username = Personal.username(gender)
        return url.format(username)

    @staticmethod
    def password(length=8, algorithm=''):
        """
        Generate a password or hash of password.

        :param length: Length of password.
        :param algorithm: Hashing algorithm.
        :returns: Password or hash of password.
        :Example:
            k6dv2odff9#4h (without hashing).
        """
        algorithm = algorithm.lower()
        punc = '!"#$%+:<?@^_'

        s = [choice(ascii_letters + digits + punc) for _ in range(length)]
        password = "".join(s).encode()

        if algorithm == 'sha1':
            return sha1(password).hexdigest()
        elif algorithm == 'sha256':
            return sha256(password).hexdigest()
        elif algorithm == 'sha512':
            return sha512(password).hexdigest()
        elif algorithm == 'md5':
            return md5(password).hexdigest()
        else:
            return password

    @staticmethod
    def email(gender='female'):
        """
        Generate a random email.

        :param gender: Gender of the user.
        :returns: Email address.
        :Example:
            foretime10@live.com
        """
        name = Personal.username(gender)
        email = name + choice(common.EMAIL_DOMAINS)
        return email.strip()

    def home_page(self, gender='female'):
        """
        Generate a random home page.

        :param gender: Gender of author of site.
        :returns: Random home page.
        :Example:
            http://www.font6.info
        """
        url = 'http://www.' + self.username(gender)
        domain = choice(common.DOMAINS)
        return '{}{}'.format(url, domain)

    @staticmethod
    def subreddit(nsfw=False, full_url=False):
        """
        Get a random subreddit from list.

        :param nsfw: NSFW subreddit.
        :param full_url: Full URL address.
        :returns: Subreddit or URL to subreddit.
        :Example:
            https://www.reddit.com/r/flask/
        """
        url = 'http://www.reddit.com'
        if not nsfw:
            if not full_url:
                return choice(common.SUBREDDITS)
            else:
                return url + choice(common.SUBREDDITS)

        nsfw = choice(common.SUBREDDITS_NSFW)
        result = url + nsfw if full_url else nsfw
        return result

    @staticmethod
    def bitcoin():
        """
        Get a random bitcoin address.
        Currently supported only two address formats that are most popular.
        It's 'P2PKH' and 'P2SH'

        :returns: Bitcoin address.
        :Example:
            3EktnHQD7RiAE6uzMj2ZifT9YgRrkSgzQX
        """
        fmt = choice(['1', '3'])
        fmt += "".join([choice(ascii_letters + digits) for _ in range(33)])
        return fmt

    @staticmethod
    def cvv():
        """
        Generate a random card verification value (CVV)

        :returns: CVV code
        :Example:
            324
        """
        return randint(100, 999)

    @staticmethod
    def credit_card_number(card_type='visa'):
        """
        Generate a random credit card number.

        :param card_type: Issuing Network. Default is Visa
        :returns: Credit card number.
        :Example:
            4455 5299 1152 2450
        """
        visa = randint(4000, 4999)
        mc = choice([randint(2221, 2720), randint(5100, 5500)])

        # Issuer identification number.
        iin = mc if card_type.lower() == 'mastercard' or 'mc' else visa

        tail = ''.join([str(randint(0000, 9999)) for _ in range(0, 3)])
        return '{} {}'.format(str(iin), tail)

    @staticmethod
    def credit_card_expiration_date(minimum=16, maximum=25):
        """
        Generate a random expiration date for credit card.

        :param minimum: Date of issue.
        :param maximum: Maximum of expiration_date.
        :returns: Expiration date of credit card.
        :Example:
            03/19.
        """
        month, year = randint(1, 12), randint(minimum, maximum)
        month = '0' + str(month) if month < 10 else month
        return '{0}/{1}'.format(month, year)

    @staticmethod
    def cid():
        """
        Generate a random CID code.

        :returns: CID code.
        :Example:
            7452
        """
        return randint(1000, 9999)

    @staticmethod
    def wmid():
        """
        Generate a identifier of user WMID for WebMoney

        :returns: WMID (WebMoney ID).
        :Example:
            834296404761
        """
        return "".join([choice(digits) for _ in range(12)])

    def paypal(self):
        """
        Generate a random PayPal account.

        :returns: Email of PapPal user.
        :Example:
            wolf235@gmail.com
        """
        return self.email()

    @staticmethod
    def yandex_money():
        """
        Generate a random Yandex.Money account.

        :returns: Yandex.Money account.
        :Example:
            97508675463414
        """
        return "".join([choice(digits) for _ in range(14)])

    def gender(self, symbol=False):
        """
        Get a random gender.

        :param symbol: Unicode symbol.
        :returns: Title of gender.
        :Example:
            Male (♂ when symbol=True).
        """
        if symbol:
            return choice(common.GENDER_SYMBOLS)

        gender = choice(self.data['gender'])
        return gender

    @staticmethod
    def height(minimum=1.5, maximum=2.0):
        """
        Generate a random height in M.

        :param minimum: Minimum value.
        :param maximum: Maximum value.
        :returns: Height.
        :Example:
            1.85.
        """
        h = uniform(float(minimum), float(maximum))
        return '{:0.2f}'.format(h)

    @staticmethod
    def weight(minimum=38, maximum=90):
        """
        Generate a random weight in KG.

        :param minimum: min value
        :param maximum: max value
        :returns: Weight.
        :Example:
            48.
        """
        w = randint(int(minimum), int(maximum))
        return w

    @staticmethod
    def blood_type():
        """
        Get a random blood type.

        :returns: Blood type (blood group).
        :Example:
            A+
        """
        return choice(common.BLOOD_GROUPS)

    def sexual_orientation(self, symbol=False):
        """
        Get a random (LOL) sexual orientation.

        :param symbol: Unicode symbol.
        :returns: Sexual orientation.
        :Example:
            Heterosexuality.
        """
        if symbol:
            return choice(common.SEXUALITY_SYMBOLS)

        sexuality = self.data['sexuality']
        return choice(sexuality)

    def occupation(self):
        """
        Get a random job.

        :returns: The name of job.
        :Example:
            Programmer.
        """
        jobs = self.data['occupation']
        return choice(jobs)

    def political_views(self):
        """
        Get a random political views.

        :returns: Political views.
        :Example:
            Liberal.
        """
        views = self.data['political_views']
        return choice(views)

    def worldview(self):
        """
        Get a random worldview.

        :returns: Worldview.
        :Example:
            Pantheism.
        """
        views = self.data['worldview']
        return choice(views)

    def views_on(self):
        """
        Get a random views on.

        :returns: Views on.
        :Example:
            Negative.
        """
        views = self.data['views_on']
        return choice(views)

    def nationality(self, gender='female'):
        """
        Get a random nationality.

        :param gender: female or male
        :returns: Nationality.
        :Example:
            Russian.
        """
        # Subtleties of the Russian orthography.
        if self.locale == 'ru':
            nations = self.data['nationality'][gender]
            return choice(nations)
        else:
            return choice(self.data['nationality'])

    def university(self):
        """
        Get a random university.

        :returns: University name.
        :Example:
            MIT.
        """
        universities = self.data['university']
        return choice(universities)

    def academic_degree(self):
        """
        Get a random academic degree.

        :returns: Degree.
        :Example:
            Bachelor.
        """
        degrees = self.data['academic_degree']
        return choice(degrees)

    def language(self):
        """
        Get a random language.

        :returns: Random language.
        :Example:
            Irish.
        """
        languages = self.data['language']
        return choice(languages)

    def favorite_movie(self):
        """
        Get a random movie for current locale.

        :returns: The name of the movie.
        :Example:
            Interstellar.
        """
        movies = self.data['favorite_movie']
        return choice(movies)

    @staticmethod
    def favorite_music_genre():
        """
        Get a random music genre.

        :returns: A music genre.
        :Example:
            Ambient.
        """
        return choice(common.FAVORITE_MUSIC_GENRE)

    @property
    def _telephone_mask(self):
        """
        It's internal method.
        Return a mask of telephone for current locale.

        :returns: A mask of telephone.
        :Example:
            +7-(###)-###-##-## (for locale ru).
        """
        masks = {
            'da': '+45 ### ### ###',
            'de': '+49-##-###-#####',
            'en': '+1-(###)-###-####',
            'es': '+34 91# ## ## ##',
            'fr': '+33-#########',
            'fi': '+358 ## ### ####',
            'is': '+354 ### ####',
            'it': '+39 6 ########',
            'nl': '+31 ## ### ####',
            'no': '+47 #### ####',
            'pt': '+351 # #### ####',
            'pt-br': '+55 (##) ####-####',
            'ru': '+7-(###)-###-##-##',
            'sv': '+46 ### ### ###',
            'default': '+#-(###)-###-####'
        }

        if self.locale in masks:
            return masks[self.locale]
        else:
            return masks['default']

    def telephone(self, mask=None, placeholder='#'):
        """
        Generate a random phone number.

        :param mask: Mask for formatting number.
        :param placeholder: A Placeholder for a mask.
            Default placeholder is sharp (#).
        :returns: Phone number.
        :Example:
            +7-(963)-409-11-22.
        """
        if not mask:
            mask = self._telephone_mask

        phone_number = ''
        for i in mask:
            phone_number += str(randint(0, 9)) \
                if i == placeholder else i
        return phone_number

    @staticmethod
    def avatar():
        """
        Get a random link to avatar.

        :returns: Link to avatar that hosted on github in
            repository of church.
        :Example:
            https://raw.githubusercontent.com/lk-geimfari/
            church/master/examples/avatars/4.png
        """
        url = common.AVATARS % randint(1, 7)
        return url

    @staticmethod
    def vehicle():
        """
        Get a random vehicle.

        :returns: A vehicle.
        :Example:
            Tesla Model S.
        """
        return choice(common.THE_VEHICLES)

    @staticmethod
    def identifier(mask='##-##/##', placeholder='#', suffix=False):
        """
        Generate a random identifier by mask. With this method you can
        generate any identifiers that you need. Simply select the mask
        that you need.

        :param mask: The mask.
        :param placeholder: Placeholder.
        :param suffix: Add characters to id.
        :return: Identifier
        :Example:
            07-97/04
        """
        suffixes = [a + b for a, b in product(ascii_uppercase, repeat=2)]
        sfx = ' %s' % choice(suffixes)

        identifier = ''
        for s in mask:
            identifier += str(randint(1, 9)) \
                if s == placeholder else s
        if suffix:
            return identifier + sfx

        return identifier


class Datetime(object):
    """
    Class for generate the fake data that you can use for
    working with date and time.
    """

    def __init__(self, locale='en'):
        """
        :param locale: Current language.
        """
        self.locale = locale
        self.data = pull('datetime.json', self.locale)

    def day_of_week(self, abbr=False):
        """
        Get a random day of week.

        :param abbr: if True then will be returned abbreviated name
            of day of the week.
        :returns: Name of day of the week.
        :Example:
            Wednesday (Wed. when abbr=True).
        """
        key = 'abbr' if abbr else 'name'
        days = self.data['day'][key]
        return choice(days)

    def month(self, abbr=False):
        """
        Get a random month.

        :param abbr: if True then will be returned
            abbreviated month name.
        :returns: Month name.
        :Example:
            January (Jan. when abbr=True).
        """
        key = 'abbr' if abbr else 'name'
        months = self.data['month'][key]
        return choice(months)

    @staticmethod
    def year(minimum=1990, maximum=2050):
        """
        Generate a random year.

        :param minimum: Minimum value.
        :param maximum: Maximum value
        :returns: Year.
        :Example:
            2023.
        """
        return randint(int(minimum), int(maximum))

    def periodicity(self):
        """
        Get a random periodicity string.

        :returns: Periodicity.
        :Example:
            Never.
        """
        return choice(self.data['periodicity'])

    @staticmethod
    def date(sep='-',minimum=2000, maximum=2035, with_time=False):
        """
        Generate a random date formatted as a 11-05-2016

        :param sep: A separator for date. Default is '-'.
        :param minimum: Minimum value of year.
        :param maximum: Maximum value of year.
        :param with_time: if it's True then will be added random time.
        :returns: Formatted date and time.
        :Example:
            20-03-2016 03:20.
        """
        d = date(randint(minimum, maximum), randint(1, 12), randint(1, 28))
        pattern = '%d{0}%m{0}%Y %m:%d' if with_time else '%d{0}%m{0}%Y'
        return d.strftime(pattern.format(sep))

    @staticmethod
    def day_of_month():
        """
        Static method for generate a random days of month, from 1 to 31.

        :returns: Random value from 1 to 31.
        :Example:
            23
        """
        return randint(1, 31)

    def birthday(self, minimum=1980, maximum=2000, readable=True, fmt=None):
        """
        Generate a random day of birth.

        :param minimum: Minimum of range
        :param maximum: Maximum of range
        :param readable: Return a user-friendly
        readable format.
        :param fmt: The format.
        :returns: A birthday.
        :Example:
            June 20, 1987
        """
        if not fmt:
            fmt = '%d-%m-%Y'

        if not readable:
            f = datetime.strptime(str(minimum), "%Y")
            t = datetime.strptime(str(maximum), "%Y")
            bd = [f + timedelta(days=x) for x in range(0, (t - f).days)]
            return choice(bd).strftime(fmt)

        return '{} {}, {}'.format(
            self.month(),
            self.day_of_month(),
            self.year(minimum, maximum)
        )


class Network(object):
    """
    Class for generate data for working with network,
    i.e IPv4, IPv6 and another
    """

    @staticmethod
    def ip_v4():
        """
        Static method for generate a random IPv4 address.

        :returns: Random IPv4 address.
        :Example:
            19.121.223.58
        """
        ip = '.'.join([str(randint(0, 255)) for _ in range(0, 4)])
        return ip

    @staticmethod
    def ip_v6():
        """
        Static method for generate a random IPv6 address.

        :returns: Random IPv6 address.
        :Example:
            2001:c244:cf9d:1fb1:c56d:f52c:8a04:94f3
        """
        n = 16 ** 4
        ip = "2001:" + ":".join("%x" % randint(0, n) for _ in range(7))
        return ip

    @staticmethod
    def mac_address():
        """
        Static method for generate a random MAC address.

        :returns: Random MAC address.
        :Example:
            00:16:3e:25:e7:b1
        """
        mac_hex = [0x00, 0x16, 0x3e,
                   randint(0x00, 0x7f),
                   randint(0x00, 0xff),
                   randint(0x00, 0xff)
                   ]
        mac = map(lambda x: "%02x" % x, mac_hex)
        return ':'.join(mac)

    @staticmethod
    def user_agent():
        """
        Get a random user agent.

        :returns: User agent.
        :Example:
            Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0)
            Gecko/20100101 Firefox/15.0.1
        """
        agent = choice(common.USER_AGENTS)
        return agent


class File(object):
    """
    Class for generate fake data for files.
     """

    @staticmethod
    def extension(file_type='text'):
        """
        Get a random extension from list.

        :param file_type: The type of extension. Default is text.

        All supported types:
            1. source - '.py', '.rb', '.cpp' and other.
            2. text = '.doc', '.log', '.rtf' and other.
            3. data = '.csv', '.dat', '.pps' and other.
            4. audio = '.mp3', '.flac', '.m4a' and other.
            5. video = '.mp4', '.m4v', '.avi' and other.
            6. image = '.jpeg', '.jpg', '.png' and other.
            7. executable = '.exe', '.apk', '.bat' and other.
            8. compressed = '.zip', '.7z', '.tar.xz' and other.

        :returns: Extension of a file.
        :Example:
            .py (When file_type='source')
        """
        k = file_type.lower()
        return choice(common.EXTENSIONS[k])


class Science(object):
    """
    Class for getting facts science.
    """

    def __init__(self, locale='en'):
        """
        :param lang: Current language.
        """
        self.locale = locale
        self._data = pull('science.json', self.locale)

    @staticmethod
    def math_formula():
        """
        Get a random mathematical formula.

        :returns: Math formula.
        :Example:
            A = (ab)/2.
        """
        formula = choice(common.MATH_FORMULAS)
        return formula

    def chemical_element(self, name_only=True):
        """
        Get a random chemical element from file.

        :param name_only: if False then will be returned dict.
        :returns: Name of chemical element or dict.
        :Example:
            {'Symbol': 'S', 'Name': 'Sulfur', 'Atomic number': '16'}
        """
        e = choice(self._data['chemical_element']).split('|')
        if not name_only:
            return {
                'name': e[0].strip(),
                'symbol': e[1].strip(),
                'atomic_number': e[2].strip()
            }
        else:
            return e[0]

    def scientific_article(self):
        """
        Get a random link to scientific article on Wikipedia.

        :returns: Link to article on Wikipedia.
        :Example:
            https://en.wikipedia.org/wiki/Black_hole
        """
        articles = self._data['article']
        return choice(articles)

    def scientist(self):
        """
        Get a random name of scientist.

        :returns: Name of scientist.
        :Example:
            Konstantin Tsiolkovsky.
        """
        scientists = self._data['scientist']
        return choice(scientists)


class Development(object):
    """
    Class for getting fake data for Developers.
    """

    @staticmethod
    def software_license():
        """
        Get a random software license from list.

        :returns: License name.
        :Example:
            The BSD 3-Clause License.
        """
        return choice(common.LICENSES)

    @staticmethod
    def version():
        """
        Generate a random version information.

        :returns: The version.
        :Example:
            0.11.3.
        """
        n = (randint(0, 11) for _ in range(3))
        return '{}.{}.{}'.format(*n)

    @staticmethod
    def database(nosql=False):
        """
        Get a random database name.

        :param nosql: only NoSQL databases.
        :returns: Database name.
        :Example:
            PostgreSQL.
        """
        if nosql:
            return choice(common.NOSQL)
        return choice(common.SQL)

    @staticmethod
    def other():
        """
        Get a random value list.

        :returns: Some other technology.
        :Example:
            Nginx.
        """
        return choice(common.OTHER_TECH)

    @staticmethod
    def programming_language():
        """
        Get a random programming language from list.

        :returns: Programming language.
        :Example:
            Erlang.
        """
        return choice(common.PROGRAMMING_LANGS)

    @staticmethod
    def framework(_type='back'):
        """
        Get a random framework from file.

        :param _type: If _type='front' then will be returned
            front-end framework, else will be returned back-end framework.
        :returns: Framework or dict of used stack
        :Example:
            Python/Django.
        """
        if _type == 'front':
            return choice(common.FRONTEND)
        else:
            return choice(common.BACKEND)

    def stack_of_tech(self, nosql=False):
        """
        Get a random stack.

        :param nosql: When nosql=True the only NoSQL skills.
        :returns: Dict of technologies.
        :Example: {'Back-end': 'Martini', 'DB': 'SQLite',
            'Front-end': 'Webpack', 'Other': 'Nginx'}
        """
        stack = {
            'front-end': self.framework('front'),
            'back-end': self.framework('back'),
            'db': self.database(nosql),
            'other': self.other()
        }

        return stack

    @staticmethod
    def os():
        """
        Get a random operating system or distributive name.

        :returns: The name of OS.
        :Example:
            Gentoo (Yes, i know that is not OS).
        """
        return choice(common.OS)

    @staticmethod
    def stackoverflow_question():
        """
        Generate a random question id for StackOverFlow
        and return url to a question.

        :returns: URL to a question.
        :Example:
            http://stackoverflow.com/questions/1726403

        """
        post_id = randint(1000000, 9999999)
        url = 'http://stackoverflow.com/questions/{0}'
        return url.format(post_id)


class Food(object):
    """
    Class for Food, i.e fruits, vegetables, berries and other.
    """

    def __init__(self, lang='en'):
        """
        :param lang: Current language.
        """
        self.lang = lang
        self._data = pull('food.json', self.lang)

    def vegetable(self):
        """
        Get a random vegetable.

        :returns: Vegetable.
        :Example:
            Tomato.
        """
        vegetables = self._data['vegetables']
        return choice(vegetables)

    def fruit_or_berry(self):
        """
        Get a random fruit_or_berry name.

        :returns: Fruit.
        :Example:
            Banana.
        """
        fruits = self._data['fruits']
        return choice(fruits)

    def dish(self):
        """
        Get a random dish for current locale.

        :returns: Dish name.
        :Example:
            Ratatouille.
        """
        dishes = self._data['dishes']
        return choice(dishes)

    def spices(self):
        """
        Get a random spices or herbs.

        :returns: Spices or herbs.
        :Example:
            Anise.
        """
        spices = self._data['spices']
        return choice(spices)

    def drink(self):
        """
        Get a random drink.

        :returns: Alcoholic drink.
        :Example:
            Vodka.
        """
        drinks = self._data['drinks']
        return choice(drinks)

    def measurement(self):
        """
        Generate measure.
        :return: Measure.
        :Example:
            1/16 teaspoon.
        """
        a, b = randint(1, 3), randint(2, 16)

        measure = choice(self._data['measurement'])
        return '%s/%s %s' % (a, b, measure)


class Hardware(object):
    """
    Class for generate data about hardware.
    """

    @staticmethod
    def resolution():
        """
        Get a random screen resolution.

        :returns: Resolution of screen.
        :Example:
            1280x720.
        """
        return choice(common.RESOLUTIONS)

    @staticmethod
    def screen_size():
        """
        Get a random size of screen in inch.

        :returns: Screen size.
        :Example:
            13″.
        """
        return choice(common.SCREEN_SIZES)

    @staticmethod
    def cpu():
        """
        Get a random CPU name.

        :returns: CPU name.
        :Example:
            Intel® Core i7.
        """
        return choice(common.CPU)

    @staticmethod
    def cpu_frequency():
        """
        Get a random frequency of CPU.

        :returns: Frequency of CPU.
        :Example:
            4.0 GHz.
        """
        cf = uniform(1.5, 4.3)
        return "{0:.1f}GHz".format(cf)

    @staticmethod
    def generation(abbr=False):
        """
        Get a random generation.

        :returns: Generation of something.
        :Example:
             6th Generation.
        """
        if not abbr:
            return choice(common.GENERATION)

        return choice(common.GENERATION_ABBR)

    @staticmethod
    def cpu_codename():
        """
        Get a random CPU code name.

        :returns: CPU code name.
        :Example:
            Cannonlake.
        """
        cn = common.CPU_CODENAMES
        return choice(cn)

    @staticmethod
    def ram_type():
        """
        Get a random RAM type.

        :returns: Type of RAM.
        :Example:
            DDR3.
        """
        tp = ('DDR2', 'DDR3', 'DDR4')
        return choice(tp)

    @staticmethod
    def ram_size():
        """
        Get a random size of RAM.

        :returns: RAM size.
        :Example:
            16GB.
        """
        sizes = ('4', '6', '8', '16', '32', '64')
        return choice(sizes) + 'GB'

    @staticmethod
    def ssd_or_hdd():
        """
        Get a random value from list.

        :returns: HDD or SSD.
        :Example:
            512GB SSD.
        """
        return choice(common.MEMORY)

    @staticmethod
    def graphics():
        """
        Get a random graphics.

        :returns: Graphics.
        :Example:
            Intel® Iris™ Pro Graphics 6200.
        """
        return choice(common.GRAPHICS)

    @staticmethod
    def manufacturer():
        """
        Get a random manufacturer.

        :returns: Manufacturer.
        :Example:
            Dell.
        """
        return choice(common.MANUFACTURERS)

    def hardware_info(self):
        """
        Get a random full information about device (laptop).

        :returns: Full information.
        :Example:
            ASUS Intel® Core i3 3rd Generation 3.50 GHz/1920x1200/12″/
            512GB HDD(7200 RPM)/DDR2-4GB/Intel® Iris™ Pro Graphics 6200.
        """
        full = '{0} {1}-{2} CPU @ {3}/{4}/{5}/{6}/{7}-{8}/{9}.'.format(
            self.manufacturer(), self.cpu(),
            self.generation(abbr=True), self.cpu_frequency(),
            self.resolution(), self.screen_size(),
            self.ssd_or_hdd(), self.ram_type(),
            self.ram_size(), self.graphics()
        )
        return full

    @staticmethod
    def phone_model():
        """
        Get a random phone model.

        :returns: Phone model.
        :Example:
            Nokia Lumia 920.
        """
        return choice(common.PHONE_MODELS)
