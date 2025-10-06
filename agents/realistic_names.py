"""
Realistic Names Database for Bookstore Agents
Provides authentic names for books, authors, customers, and employees
"""

import random

# Real book titles with their authors and genres
BOOKS_DATABASE = [
    {"title": "To Kill a Mockingbird", "author": "Harper Lee", "genre": "Fiction", "publisher": "J.B. Lippincott & Co."},
    {"title": "1984", "author": "George Orwell", "genre": "Science Fiction", "publisher": "Secker & Warburg"},
    {"title": "Pride and Prejudice", "author": "Jane Austen", "genre": "Romance", "publisher": "T. Egerton"},
    {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "genre": "Fiction", "publisher": "Charles Scribner's Sons"},
    {"title": "The Catcher in the Rye", "author": "J.D. Salinger", "genre": "Fiction", "publisher": "Little, Brown and Company"},
    {"title": "The Hobbit", "author": "J.R.R. Tolkien", "genre": "Fantasy", "publisher": "George Allen & Unwin"},
    {"title": "Harry Potter and the Sorcerer's Stone", "author": "J.K. Rowling", "genre": "Fantasy", "publisher": "Bloomsbury"},
    {"title": "The Lord of the Rings", "author": "J.R.R. Tolkien", "genre": "Fantasy", "publisher": "George Allen & Unwin"},
    {"title": "The Da Vinci Code", "author": "Dan Brown", "genre": "Mystery", "publisher": "Doubleday"},
    {"title": "The Alchemist", "author": "Paulo Coelho", "genre": "Fiction", "publisher": "HarperCollins"},
    {"title": "The Book Thief", "author": "Markus Zusak", "genre": "Historical Fiction", "publisher": "Picador"},
    {"title": "The Hunger Games", "author": "Suzanne Collins", "genre": "Science Fiction", "publisher": "Scholastic Press"},
    {"title": "The Chronicles of Narnia", "author": "C.S. Lewis", "genre": "Fantasy", "publisher": "Geoffrey Bles"},
    {"title": "Brave New World", "author": "Aldous Huxley", "genre": "Science Fiction", "publisher": "Chatto & Windus"},
    {"title": "The Shining", "author": "Stephen King", "genre": "Horror", "publisher": "Doubleday"},
    {"title": "Gone with the Wind", "author": "Margaret Mitchell", "genre": "Historical Fiction", "publisher": "Macmillan Publishers"},
    {"title": "The Fault in Our Stars", "author": "John Green", "genre": "Young Adult", "publisher": "Dutton Books"},
    {"title": "Twilight", "author": "Stephenie Meyer", "genre": "Romance", "publisher": "Little, Brown and Company"},
    {"title": "The Girl with the Dragon Tattoo", "author": "Stieg Larsson", "genre": "Mystery", "publisher": "Norstedts Förlag"},
    {"title": "The Help", "author": "Kathryn Stockett", "genre": "Historical Fiction", "publisher": "Penguin Books"},
    {"title": "Life of Pi", "author": "Yann Martel", "genre": "Adventure", "publisher": "Knopf Canada"},
    {"title": "The Kite Runner", "author": "Khaled Hosseini", "genre": "Fiction", "publisher": "Riverhead Books"},
    {"title": "Sapiens", "author": "Yuval Noah Harari", "genre": "Non-Fiction", "publisher": "Harvill Secker"},
    {"title": "Educated", "author": "Tara Westover", "genre": "Biography", "publisher": "Random House"},
    {"title": "Becoming", "author": "Michelle Obama", "genre": "Biography", "publisher": "Crown Publishing"},
    {"title": "Where the Crawdads Sing", "author": "Delia Owens", "genre": "Mystery", "publisher": "G.P. Putnam's Sons"},
    {"title": "The Silent Patient", "author": "Alex Michaelides", "genre": "Thriller", "publisher": "Celadon Books"},
    {"title": "Atomic Habits", "author": "James Clear", "genre": "Self-Help", "publisher": "Avery"},
    {"title": "The Subtle Art of Not Giving a F*ck", "author": "Mark Manson", "genre": "Self-Help", "publisher": "HarperOne"},
    {"title": "Thinking, Fast and Slow", "author": "Daniel Kahneman", "genre": "Psychology", "publisher": "Farrar, Straus and Giroux"},
    {"title": "The Power of Now", "author": "Eckhart Tolle", "genre": "Spirituality", "publisher": "New World Library"},
    {"title": "The 7 Habits of Highly Effective People", "author": "Stephen Covey", "genre": "Self-Help", "publisher": "Free Press"},
    {"title": "Dune", "author": "Frank Herbert", "genre": "Science Fiction", "publisher": "Chilton Books"},
    {"title": "Foundation", "author": "Isaac Asimov", "genre": "Science Fiction", "publisher": "Gnome Press"},
    {"title": "Ender's Game", "author": "Orson Scott Card", "genre": "Science Fiction", "publisher": "Tor Books"},
    {"title": "The Martian", "author": "Andy Weir", "genre": "Science Fiction", "publisher": "Crown Publishing"},
    {"title": "Ready Player One", "author": "Ernest Cline", "genre": "Science Fiction", "publisher": "Crown Publishing"},
    {"title": "The Road", "author": "Cormac McCarthy", "genre": "Post-Apocalyptic", "publisher": "Alfred A. Knopf"},
    {"title": "The Handmaid's Tale", "author": "Margaret Atwood", "genre": "Dystopian", "publisher": "McClelland & Stewart"},
    {"title": "The Outsiders", "author": "S.E. Hinton", "genre": "Young Adult", "publisher": "Viking Press"},
    {"title": "A Thousand Splendid Suns", "author": "Khaled Hosseini", "genre": "Fiction", "publisher": "Riverhead Books"},
    {"title": "The Nightingale", "author": "Kristin Hannah", "genre": "Historical Fiction", "publisher": "St. Martin's Press"},
    {"title": "Eleanor Oliphant Is Completely Fine", "author": "Gail Honeyman", "genre": "Fiction", "publisher": "HarperCollins"},
    {"title": "The Lovely Bones", "author": "Alice Sebold", "genre": "Fiction", "publisher": "Little, Brown and Company"},
    {"title": "Big Little Lies", "author": "Liane Moriarty", "genre": "Mystery", "publisher": "G.P. Putnam's Sons"},
    {"title": "The Perks of Being a Wallflower", "author": "Stephen Chbosky", "genre": "Young Adult", "publisher": "MTV Books"},
    {"title": "Me Before You", "author": "Jojo Moyes", "genre": "Romance", "publisher": "Penguin Books"},
    {"title": "The Five People You Meet in Heaven", "author": "Mitch Albom", "genre": "Fiction", "publisher": "Hyperion"},
    {"title": "Tuesdays with Morrie", "author": "Mitch Albom", "genre": "Biography", "publisher": "Doubleday"},
    {"title": "Wild", "author": "Cheryl Strayed", "genre": "Biography", "publisher": "Alfred A. Knopf"},
    {"title": "Eat, Pray, Love", "author": "Elizabeth Gilbert", "genre": "Biography", "publisher": "Viking Press"},
    {"title": "The Glass Castle", "author": "Jeannette Walls", "genre": "Biography", "publisher": "Scribner"},
    {"title": "Into the Wild", "author": "Jon Krakauer", "genre": "Non-Fiction", "publisher": "Villard"},
    {"title": "The Immortal Life of Henrietta Lacks", "author": "Rebecca Skloot", "genre": "Non-Fiction", "publisher": "Crown Publishing"},
    {"title": "Born a Crime", "author": "Trevor Noah", "genre": "Biography", "publisher": "Spiegel & Grau"},
    {"title": "The Color Purple", "author": "Alice Walker", "genre": "Fiction", "publisher": "Harcourt Brace Jovanovich"},
    {"title": "Beloved", "author": "Toni Morrison", "genre": "Fiction", "publisher": "Alfred A. Knopf"},
    {"title": "One Hundred Years of Solitude", "author": "Gabriel García Márquez", "genre": "Magical Realism", "publisher": "Harper & Row"},
    {"title": "The Name of the Wind", "author": "Patrick Rothfuss", "genre": "Fantasy", "publisher": "DAW Books"},
    {"title": "A Game of Thrones", "author": "George R.R. Martin", "genre": "Fantasy", "publisher": "Bantam Spectra"},
    {"title": "Mistborn", "author": "Brandon Sanderson", "genre": "Fantasy", "publisher": "Tor Books"},
    {"title": "The Way of Kings", "author": "Brandon Sanderson", "genre": "Fantasy", "publisher": "Tor Books"},
    {"title": "The Shadow of the Wind", "author": "Carlos Ruiz Zafón", "genre": "Mystery", "publisher": "Planeta"},
    {"title": "The Secret History", "author": "Donna Tartt", "genre": "Mystery", "publisher": "Alfred A. Knopf"},
    {"title": "Sharp Objects", "author": "Gillian Flynn", "genre": "Thriller", "publisher": "Shaye Areheart Books"},
    {"title": "Gone Girl", "author": "Gillian Flynn", "genre": "Thriller", "publisher": "Crown Publishing"},
    {"title": "The Woman in the Window", "author": "A.J. Finn", "genre": "Thriller", "publisher": "William Morrow"},
    {"title": "Before I Go to Sleep", "author": "S.J. Watson", "genre": "Thriller", "publisher": "Harper"},
    {"title": "The Girl on the Train", "author": "Paula Hawkins", "genre": "Thriller", "publisher": "Riverhead Books"},
    {"title": "Dark Places", "author": "Gillian Flynn", "genre": "Thriller", "publisher": "Shaye Areheart Books"},
    {"title": "In Cold Blood", "author": "Truman Capote", "genre": "True Crime", "publisher": "Random House"},
    {"title": "The Devil in the White City", "author": "Erik Larson", "genre": "Historical Non-Fiction", "publisher": "Crown Publishers"},
    {"title": "Unbroken", "author": "Laura Hillenbrand", "genre": "Biography", "publisher": "Random House"},
    {"title": "The Boys in the Boat", "author": "Daniel James Brown", "genre": "Non-Fiction", "publisher": "Viking Press"},
    {"title": "The Wright Brothers", "author": "David McCullough", "genre": "Biography", "publisher": "Simon & Schuster"},
    {"title": "Steve Jobs", "author": "Walter Isaacson", "genre": "Biography", "publisher": "Simon & Schuster"},
    {"title": "Einstein: His Life and Universe", "author": "Walter Isaacson", "genre": "Biography", "publisher": "Simon & Schuster"},
    {"title": "The Diary of a Young Girl", "author": "Anne Frank", "genre": "Biography", "publisher": "Contact Publishing"},
    {"title": "Long Walk to Freedom", "author": "Nelson Mandela", "genre": "Biography", "publisher": "Little, Brown and Company"},
    {"title": "I Know Why the Caged Bird Sings", "author": "Maya Angelou", "genre": "Biography", "publisher": "Random House"},
    {"title": "The Autobiography of Malcolm X", "author": "Malcolm X & Alex Haley", "genre": "Biography", "publisher": "Grove Press"},
    {"title": "When Breath Becomes Air", "author": "Paul Kalanithi", "genre": "Biography", "publisher": "Random House"},
    {"title": "The Last Lecture", "author": "Randy Pausch", "genre": "Biography", "publisher": "Hyperion"},
    {"title": "Man's Search for Meaning", "author": "Viktor Frankl", "genre": "Psychology", "publisher": "Beacon Press"},
    {"title": "Quiet", "author": "Susan Cain", "genre": "Psychology", "publisher": "Crown Publishing"},
    {"title": "Grit", "author": "Angela Duckworth", "genre": "Psychology", "publisher": "Scribner"},
    {"title": "Outliers", "author": "Malcolm Gladwell", "genre": "Non-Fiction", "publisher": "Little, Brown and Company"},
    {"title": "The Tipping Point", "author": "Malcolm Gladwell", "genre": "Non-Fiction", "publisher": "Little, Brown and Company"},
    {"title": "Blink", "author": "Malcolm Gladwell", "genre": "Non-Fiction", "publisher": "Little, Brown and Company"},
    {"title": "Freakonomics", "author": "Steven Levitt & Stephen Dubner", "genre": "Economics", "publisher": "William Morrow"},
    {"title": "The Lean Startup", "author": "Eric Ries", "genre": "Business", "publisher": "Crown Business"},
    {"title": "Good to Great", "author": "Jim Collins", "genre": "Business", "publisher": "HarperBusiness"},
    {"title": "The Innovator's Dilemma", "author": "Clayton Christensen", "genre": "Business", "publisher": "Harvard Business Review Press"},
]

# Customer first names (diverse and international)
CUSTOMER_FIRST_NAMES = [
    "Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason", "Isabella", "William",
    "Mia", "James", "Charlotte", "Benjamin", "Amelia", "Lucas", "Harper", "Henry", "Evelyn", "Alexander",
    "Abigail", "Michael", "Emily", "Daniel", "Elizabeth", "Matthew", "Sofia", "Jackson", "Avery", "Sebastian",
    "Ella", "David", "Scarlett", "Joseph", "Grace", "Carter", "Chloe", "Owen", "Victoria", "Wyatt",
    "Riley", "John", "Aria", "Jack", "Lily", "Luke", "Aubrey", "Jayden", "Zoey", "Dylan",
    "Penelope", "Grayson", "Layla", "Levi", "Nora", "Isaac", "Hannah", "Gabriel", "Lillian", "Julian",
    "Addison", "Mateo", "Eleanor", "Anthony", "Natalie", "Jaxon", "Luna", "Lincoln", "Savannah", "Joshua",
    "Brooklyn", "Christopher", "Leah", "Andrew", "Zoe", "Theodore", "Stella", "Caleb", "Hazel", "Ryan",
    "Ellie", "Asher", "Paisley", "Nathan", "Audrey", "Thomas", "Skylar", "Leo", "Violet", "Isaiah",
    "Claire", "Charles", "Bella", "Josiah", "Aurora", "Hudson", "Lucy", "Christian", "Anna", "Hunter"
]

# Customer last names (diverse)
CUSTOMER_LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
    "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker", "Cruz", "Edwards", "Collins", "Reyes",
    "Stewart", "Morris", "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper",
    "Peterson", "Bailey", "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson",
    "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes",
    "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long", "Ross", "Foster", "Jimenez"
]

# Employee first names
EMPLOYEE_FIRST_NAMES = [
    "Sarah", "Michael", "Jennifer", "Christopher", "Amanda", "Matthew", "Jessica", "Joshua", "Ashley", "David",
    "Stephanie", "Daniel", "Nicole", "Andrew", "Elizabeth", "Ryan", "Michelle", "Brandon", "Kimberly", "Jason",
    "Amy", "Justin", "Melissa", "Kevin", "Rebecca", "Eric", "Rachel", "Brian", "Lauren", "Tyler",
    "Samantha", "Jacob", "Heather", "Nicholas", "Maria", "Kyle", "Brittany", "Aaron", "Megan", "Adam",
    "Christina", "Jonathan", "Angela", "Steven", "Alexis", "Timothy", "Laura", "Sean", "Danielle", "Patrick",
    "Katherine", "Charles", "Victoria", "Jordan", "Andrea", "Nathan", "Monica", "Austin", "Jasmine", "Robert",
    "Diana", "Richard", "Natalie", "Thomas", "Vanessa", "Alex", "Catherine", "Peter", "Shannon", "Gregory"
]

# Employee last names
EMPLOYEE_LAST_NAMES = [
    "Anderson", "Martinez", "Thompson", "Garcia", "Robinson", "Rodriguez", "Lewis", "Walker", "Hall", "Allen",
    "Young", "King", "Wright", "Lopez", "Hill", "Scott", "Green", "Adams", "Baker", "Nelson",
    "Carter", "Mitchell", "Perez", "Roberts", "Turner", "Phillips", "Campbell", "Parker", "Evans", "Edwards",
    "Collins", "Stewart", "Sanchez", "Morris", "Rogers", "Reed", "Cook", "Morgan", "Bell", "Murphy",
    "Bailey", "Rivera", "Cooper", "Richardson", "Cox", "Howard", "Ward", "Torres", "Peterson", "Gray",
    "Ramirez", "James", "Watson", "Brooks", "Kelly", "Sanders", "Price", "Bennett", "Wood", "Barnes",
    "Ross", "Henderson", "Coleman", "Jenkins", "Perry", "Powell", "Long", "Patterson", "Hughes", "Flores"
]

# Employee roles
EMPLOYEE_ROLES = [
    "Store Manager",
    "Assistant Manager",
    "Inventory Manager",
    "Sales Associate",
    "Customer Service Representative",
    "Cashier",
    "Book Buyer",
    "Events Coordinator",
    "Marketing Specialist",
    "Warehouse Supervisor"
]


def get_random_book_info(index=None):
    """Get a random book or specific book by index."""
    if index is not None and 0 <= index < len(BOOKS_DATABASE):
        book = BOOKS_DATABASE[index % len(BOOKS_DATABASE)]
    else:
        book = random.choice(BOOKS_DATABASE)
    return book.copy()


def get_random_customer_name():
    """Generate a random customer full name."""
    first_name = random.choice(CUSTOMER_FIRST_NAMES)
    last_name = random.choice(CUSTOMER_LAST_NAMES)
    return f"{first_name} {last_name}"


def get_random_employee_name():
    """Generate a random employee full name."""
    first_name = random.choice(EMPLOYEE_FIRST_NAMES)
    last_name = random.choice(EMPLOYEE_LAST_NAMES)
    return f"{first_name} {last_name}"


def get_random_employee_role():
    """Get a random employee role."""
    return random.choice(EMPLOYEE_ROLES)


def assign_book_names(book_agent, book_index):
    """
    Assign realistic book information to a book agent.
    
    Args:
        book_agent: The BookAgent instance
        book_index: Index of the book for consistent assignment
    """
    book_info = get_random_book_info(book_index)
    book_agent.title = book_info["title"]
    book_agent.author = book_info["author"]
    book_agent.genre = book_info["genre"]
    book_agent.genres = [book_info["genre"]]
    book_agent.publisher = book_info["publisher"]
    

def assign_customer_name(customer_agent):
    """
    Assign a realistic name to a customer agent.
    
    Args:
        customer_agent: The CustomerAgent instance
    """
    customer_agent.name = get_random_customer_name()


def assign_employee_name(employee_agent):
    """
    Assign a realistic name and role to an employee agent.
    
    Args:
        employee_agent: The EmployeeAgent instance
    """
    employee_agent.name = get_random_employee_name()
    if not hasattr(employee_agent, 'role') or employee_agent.role == "Manager":
        employee_agent.role = get_random_employee_role()
