from __init__ import CURSOR, CONN
from employee import Employee

class Review:
    all = {}  # Dictionary to store all Review instances

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, year):
        if isinstance(year, int) and year >= 2000:
            self._year = year
        else:
            raise ValueError("Year must be an integer greater than or equal to 2000.")

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, summary):
        if isinstance(summary, str) and len(summary) > 0:
            self._summary = summary
        else:
            raise ValueError("Summary must be a non-empty string.")

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, employee_id):
        if isinstance(employee_id, int) and Employee.find_by_id(employee_id):
            self._employee_id = employee_id
        else:
            raise ValueError("employee_id must reference a valid employee in the database.")

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """Insert or update the row in the table with the current Review object's data."""
        if self.id:  # If the Review already exists, update it
            self.update()
        else:  # Else, insert it
            sql = """
                INSERT INTO reviews (year, summary, employee_id) 
                VALUES (?, ?, ?);
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
            self.id = CURSOR.lastrowid
            Review.all[self.id] = self
            CONN.commit()

    @classmethod
    def create(cls, year, summary, employee_id):
        """ Initialize a new Review instance and save the object to the database. Return the new instance. """
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        """Return a Review instance having the attribute values from the table row."""
        review = cls.all.get(row[0])
        if review:
            # Ensure that the instance's attributes are updated with the database values
            review.year = row[1]
            review.summary = row[2]
            review.employee_id = row[3]
        else:
            review = cls(row[1], row[2], row[3], row[0])
            cls.all[review.id] = review
        return review

    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance corresponding to the specified primary key."""
        sql = "SELECT * FROM reviews WHERE id = ?;"
        CURSOR.execute(sql, (id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    @classmethod
    def get_all(cls):
        """Return a list of all Review instances."""
        sql = "SELECT * FROM reviews;"
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    def update(self):
        """Update the corresponding row in the database with the current Review instance's data."""
        sql = """
            UPDATE reviews 
            SET year = ?, summary = ?, employee_id = ? 
            WHERE id = ?;
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        """Delete the corresponding row in the database and remove the instance from the dictionary."""
        sql = "DELETE FROM reviews WHERE id = ?;"
        CURSOR.execute(sql, (self.id,))
        del Review.all[self.id]
        self.id = None
        CONN.commit()
        

