from django.core.management.base import BaseCommand
from Course.models import Course

class Command(BaseCommand):
    help = 'Populates database with demo data'

    def handle(self, *args, **options):
        import_courses()


def import_courses():
    print("import courses")
    print('adding course gsi')
    gsi = Course(
        title='Gesellschaftliche Spannungsfelder der Informatik',
        short_title='gsi',
        description= """/
Ziele der Lehrveranstaltung
Verständnis für die gesellschaftlichen Spannungsfelder der Informatik; Fähigkeit, mehrere Perspektiven von Problemstellungen zu sehen und entsprechend Fragen aus unterschiedlichen Sichtweisen stellen und beantworten zu können; Grundlegende Kenntnisse aus den Bereichen Sicherheit von Informationssystemen, Kryptographie, Lizenz- und Patentrecht.

Inhalt der Lehrveranstaltung
Selbstverständnis, Geschichte und Stimmen der Informatik als Technologie und akademische Disziplin. Globalisierung und Vernetzung: Geschichte und Struktur des Internet, Monopolisierung, Digital Divide und Gegenkulturen der IKT-Industrie. Geschichte, Visionen und Realität der Informationsgesellschaft und daraus folgende Änderungen der Wissensordnung. Verletzlichkeit der Informationsgesellschaft: Spannungsfeld "Sicherheit vs. Freiheit" , Überwachungstechnologien im gesellschaftlichen Kontext, Angriffe auf die Privatsphäre sowie gesetzliche, organisatorische und technische Schutzmaßnahmen, Anwendungen der Kryptographie. Copyright und Intellectual Property: Problemfelder, Organisationen und Auseinandersetzungen aus Urheberrecht und Patentpraxis, Free and Open Source Software, Creative Commons. Die Lehrveranstaltung ist als offene, portfoliobasierte Unterrichtsform konzipiert. Teilnehmer/innen wählen aus einem Katalog mögliche Aktivitäten nach eigenen Kriterien aus, arbeiten diese aus und geben sie über ein Portfolio-System ab, das laufend beurteilt wird. Zur Erreichung einer positiven Note ist eine Mindestzahl von Punkten zu erreichen. Die Inhalte werden vorwiegend in Form einer Frontalvorlesung vermittelt, die aber mittels neuer Medien interaktiv gestaltet ist.
""",
        course_number='187.237',
    )
    gsi.save()

    print('adding course bhci')
    hci = Course(
        title='Basics of Human Computer Interaction',
        short_title='bhci',
        description = """/
Ziele der Lehrveranstaltung
Work in teams on reflection and design problems; Be able to discuss technologies and needs with potential users; Come up with innovative ideas for interactive technologies; Approach open and ambiguous problem situations in a proactive and self-organized way.

Inhalt der Lehrveranstaltung
Theories of Human perception, cognition and practice
Theoretical foundation of user experience
Design principles and interface design guidelines
Conducting usability studies and expert evaluations of interactive systems
Principles of a user centred interaction design process
HCI related to different types of interactive software
""",
        course_number='187.A21',
    )
    hci.save()