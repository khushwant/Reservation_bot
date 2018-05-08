from google.appengine.ext import ndb

# These environment variables are configured in app.yaml.

class Bookings(ndb.Model):
    booking_no = ndb.IntegerProperty(required=True)
    name = ndb.StringProperty(required=True)
    email = ndb.KeyProperty(required=True)
    table_no = ndb.IntegerProperty()
    confirm = ndb.IntegerProperty(default=None)
    owner = ndb.IntegerProperty()

class Logs(ndb.Model):
    log_txt = ndb.StringProperty(indexed=True)

class DBHelper:

    def add_email(self, email, owner):
        booking = Bookings()
        # stmt = "INSERT INTO bookings (name, owner) VALUES (%s, %s)"
        # args = (name, owner)
        key_a = ndb.Key(Bookings, email);
        booking = Bookings(key=key_a)
        booking.put()
        # booking.email = email
        booking.owner = owner
        booking.put()
        booking.booking_no = self.key().id()
        booking.put()

    def add_name(self, name, owner):
        # stmt = "UPDATE bookings SET email = (%s) WHERE owner = (%s)"
        # args = (email, owner)
        booking = Bookings.query()
        searchquery = booking.filter(Bookings.owner == owner)
        for i in searchquery:
            i.name = name
            i.put()

    def add_table_booking(self, table_no, owner):
        # stmt = "UPDATE bookings SET table_no = (%s) WHERE owner = (%s)"
        # args = (table_no, owner)
        booking = Bookings.query()
        searchquery = booking.filter(Bookings.owner == owner)
        for i in searchquery:
            i.table_no = table_no
            i.put()

    def delete_booking(self, owner):
        # stmt = "DELETE FROM bookings WHERE owner = (%s)"
        # args = (owner,)
        booking = Bookings.query()
        searchquery = booking.filter(Bookings.owner == owner)
        for i in searchquery:
            i.key.delete()

    def confirm_booking(self, owner):
        # stmt = "UPDATE bookings SET confirm = (%s) WHERE owner = (%s)"
        # args = (1, owner)
        booking = Bookings.query()
        searchquery = booking.filter(Bookings.owner == owner)
        for i in searchquery:
            i.confirm = 1
            i.put()

    def get_booked_tables(self):
        # stmt = "SELECT DISTINCT table_no FROM bookings WHERE confirm = (%s)"
        # args = (1,)
        booking = Bookings.query()
        searchquery = booking.filter(Bookings.confirm == 1)
        table_list = []
        for i in searchquery:
            if i.table_no not in table_list:
                table_list.append(i.table_no)
        return [x for x in table_list]

    def get_bookings(self, owner):
        # stmt = "SELECT * FROM bookings WHERE owner = (%s)"
        # args = (owner,)
        booking = Bookings.query()
        searchquery = booking.filter(Bookings.owner == owner)
        return [x for x in searchquery]

    def get_all(self):
        booking = Bookings.query()
        logs = Logs.query()

        return (booking, logs)

    def add_log(self, log_text):
        # stmt = "INSERT INTO logs VALUES (%s)"
        # args = (log_text,)
        logs = Logs()
        logs.log_txt = log_text
        logs.put()

