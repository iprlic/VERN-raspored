import click
import logging.config
from config import LOGGING, STUDOMATIC_URL
from session import ScrapeSession
from lxml import html
import datetime

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('studomatic-scrapper')

class Scrapper(object):
    schedule = []
    viewState = None
    eventValidation = None
    viewStateGenerator = None

    def __init__(self, username, password, weeks, wait=None):
        logger.info('Started scrapper for user %s' % username)
        self.schedule = []
        self.today = datetime.date.today()
        self.last_monday = self.today - datetime.timedelta(days=self.today.weekday())
        self.weeks = weeks
        self.html_parser = html.HTMLParser(encoding='windows-1250')
        self.session = ScrapeSession(wait=wait)
        self.init_session()
        self.login(username, password)
        self.fetchSchedule()
        self.generateCalendar()


    def init_session(self):
        self.session.get(STUDOMATIC_URL)

    def fetchSchedule(self):
        monday = self.last_monday
        weekCnt = 1

        weekScheduleFirstPage = self.session.get(STUDOMATIC_URL + '/Raspored.aspx')
        self.extractViewState(weekScheduleFirstPage)

        while weekCnt <= self.weeks:
            weekSchedulePage = self.session.post(STUDOMATIC_URL + '/Raspored.aspx',
                                                    {
                                                        '__EVENTTARGET': 'puiDatum',
                                                        '__EVENTARGUMENT': '',
                                                        '__LASTFOCUS': '',
                                                        '__VIEWSTATE': self.viewState,
                                                        '__VIEWSTATEGENERATOR': self.viewStateGenerator,
                                                        '__EVENTVALIDATION': self.eventValidation,
                                                        'puiDatum': 'ponedjeljak, ' + monday.strftime('%d. %m. %Y.'),

                                                    }
                                                 )

            weekSchedulePageHtml = html.fromstring(weekSchedulePage.content, parser=self.html_parser)
            classes = weekSchedulePageHtml.xpath('//table[@class="raspored"]//table/tr')

            for cls in classes:
                classInfo = cls.xpath('./td')[0].xpath('.//text()')
                classDate = str(classInfo[0]).strip()
                classTime = str(classInfo[1]).strip()
                classLocation = str(classInfo[2]).strip()

                classDescription = cls.xpath('./td')[1].xpath('.//text()')
                classProfessor = str(classDescription[0]).strip()
                className = str(classDescription[2]).strip()
                classType = str(classDescription[4]).strip()
                classAdditionalInfo = str(classDescription[5]).strip()

                self.schedule.append({
                    'date': classDate,
                    'time': classTime,
                    'date_time': datetime.datetime.strptime(classDate + ' ' + classTime, '%d.%m.%Y. %H:%M'),
                    'location': classLocation,
                    'professor': classProfessor,
                    'name': className,
                    'type': classType,
                    'additional_info': classAdditionalInfo
                })

            self.extractViewState(weekSchedulePage)
            weekCnt += 1
            monday += datetime.timedelta(days=7)

    def extractViewState(self, response):
        responseHtml = html.fromstring(response.content)

        if len(responseHtml.xpath('//input[@id="__VIEWSTATE"]/@value')) > 0:
            self.viewState = str(responseHtml.xpath('//input[@id="__VIEWSTATE"]/@value')[0])
        else:
            self.viewState = None

        if len(responseHtml.xpath('//input[@id="__EVENTVALIDATION"]/@value')) > 0:
            self.eventValidation = str(responseHtml.xpath('//input[@id="__EVENTVALIDATION"]/@value')[0])
        else:
            self.eventValidation = None

        if len(responseHtml.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value')) > 0:
            self.viewStateGenerator = str(responseHtml.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value')[0])
        else:
            self.viewStateGenerator = None

    def login(self, username, password):
        loginPage = self.session.get(STUDOMATIC_URL)
        self.extractViewState(loginPage)

        startPage = self.session.post(STUDOMATIC_URL + 'Login.aspx?ReturnUrl=%2fvern-student%2fdefault.aspx',
                          {
                            'login': username,
                            'password': password,
                            'butSubmit.x':'37',
                            'butSubmit.y':'22',
                            'butSubmit':'Prijava',
                            '__EVENTVALIDATION': self.eventValidation,
                            '__VIEWSTATEGENERATOR': self.viewStateGenerator,
                            '__VIEWSTATE': self.viewState
                          })
        self.extractViewState(startPage)

    def generateCalendar(self):
        pass

@click.command()
@click.option( '--username',  prompt=True, help='Studomatic username')
@click.option('--password', prompt=True, hide_input=True, help='Studomatic password')
@click.option('--weeks', default=20, help='Number of weeks ahead to scrape. Default is 40.')
@click.option('--wait', default=1, type=float, help='Minimum time in seconds to wait in between requests'
                                                    ' for the session. Default is 1 second.')
def cli(*args, **kwargs):
    Scrapper(*args, **kwargs)

if __name__ == '__main__':
    cli()
