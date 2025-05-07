from members.models import FamousPerson

famous_person = FamousPerson(name="John Doe", difficulty="easy", gender="male", skin_color="white")
famous_person.image = ""
famous_person.save()
