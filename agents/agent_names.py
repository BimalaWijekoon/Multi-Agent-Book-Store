"""
Sri Lankan names database for agent initialization.
Provides authentic Sri Lankan names for customers and employees.
"""

import random

# Sri Lankan first names - Sinhalese, Tamil, and Muslim names
FIRST_NAMES = [
    # Sinhalese Male names
    "Nimal", "Sunil", "Kamal", "Anil", "Bandula", "Chaminda", "Dharmasena", "Gamini", "Indika", "Janaka",
    "Kumara", "Lakshman", "Mahinda", "Nalaka", "Pradeep", "Roshan", "Sampath", "Tharanga", "Upul", "Wasantha",
    "Anura", "Chathura", "Dilshan", "Gayan", "Hashan", "Isuru", "Kasun", "Maduranga", "Nuwan", "Pathum",
    # Sinhalese Female names
    "Kumari", "Anusha", "Chathuri", "Dilini", "Gayani", "Hashini", "Ishara", "Janani", "Kavitha", "Lakshmi",
    "Madhavi", "Niluka", "Padma", "Rajini", "Sachini", "Thilini", "Udari", "Vindya", "Yamuna", "Sasika",
    "Ayesha", "Bhagya", "Chandima", "Deepika", "Erandi", "Fathima", "Ganga", "Hiruni", "Iresha", "Jayani",
    # Tamil Male names
    "Arun", "Dinesh", "Ganesh", "Karthik", "Mahesh", "Naveen", "Praveen", "Rajesh", "Suresh", "Vinod",
    "Kumar", "Ravi", "Vijay", "Prakash", "Ramesh", "Senthil", "Thilak", "Vimal", "Yogesh", "Sanjay",
    # Tamil Female names
    "Anjali", "Deepa", "Geetha", "Kavitha", "Meena", "Nisha", "Priya", "Rekha", "Shanthi", "Uma",
    "Vasanthi", "Kamala", "Lalitha", "Mala", "Nirmala", "Radha", "Saroja", "Thara", "Vani", "Yamini",
    # Muslim names
    "Mohamed", "Abdul", "Rizwan", "Farhan", "Imran", "Nawaz", "Riyaz", "Shafraz", "Yasir", "Zubair",
    "Fathima", "Ayesha", "Hafsa", "Mariam", "Nusrath", "Raihana", "Sabrina", "Zainab", "Amina", "Rizana"
]

# Sri Lankan last names - Sinhalese, Tamil, and Muslim surnames
LAST_NAMES = [
    # Sinhalese surnames
    "Fernando", "Silva", "Perera", "Mendis", "Jayawardena", "Gunasekara", "Wickramasinghe", "Rajapaksa", "Ranatunga", "Jayasuriya",
    "Bandara", "De Silva", "Dissanayake", "Gunawardena", "Herath", "Karunaratne", "Liyanage", "Munasinghe", "Ratnayake", "Senanayake",
    "Amarasinghe", "Edirisinghe", "Pathirana", "Weerasinghe", "Wijesinghe", "Abeysekara", "Samarasinghe", "Kumaratunga", "Weerasekara", "Jayakody",
    "Peiris", "Nanayakkara", "Jayasinghe", "Wickremasinghe", "Ranawaka", "Sugathadasa", "Ekanayake", "Gamage", "De Alwis", "Weerakoon",
    # Tamil surnames
    "Kumar", "Prabakaran", "Sivakumar", "Chandrasekaran", "Mahendran", "Nadarajah", "Rajaratnam", "Selvarajah", "Suntharalingam", "Thambipillai",
    "Kandasamy", "Loganathan", "Muralidharan", "Nadarajan", "Ramanathan", "Shanmuganathan", "Sivasubramaniam", "Subramaniam", "Thiruchelvam", "Varatharajah",
    # Muslim surnames
    "Mohamed", "Noordeen", "Ismail", "Ibrahim", "Cassim", "Marikar", "Saheed", "Farook", "Hameed", "Jameel",
    "Azeez", "Rasheed", "Careem", "Rameez", "Rizan", "Shukri", "Thowfeek", "Wazeer", "Yusuf", "Zahir"
]

# Employee title prefixes for more professional names
EMPLOYEE_TITLES = [
    "Mr.", "Ms.", "Mrs.", "Dr.", "Prof."
]


def generate_customer_name():
    """
    Generate a realistic customer name.
    Returns: Full name as string (e.g., "Jennifer Martinez")
    """
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    return f"{first} {last}"


def generate_employee_name(include_title=False):
    """
    Generate a realistic employee name.
    
    Args:
        include_title: If True, adds a professional title prefix
    
    Returns: Full name as string (e.g., "Ms. Sarah Chen" or "Michael Brown")
    """
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    
    if include_title and random.random() < 0.7:  # 70% chance to include title
        title = random.choice(EMPLOYEE_TITLES)
        return f"{title} {first} {last}"
    
    return f"{first} {last}"


def generate_unique_names(count, name_type="customer"):
    """
    Generate a list of unique names.
    
    Args:
        count: Number of names to generate
        name_type: "customer" or "employee"
    
    Returns: List of unique names
    """
    names = set()
    max_attempts = count * 10  # Prevent infinite loop
    attempts = 0
    
    while len(names) < count and attempts < max_attempts:
        if name_type == "employee":
            name = generate_employee_name(include_title=True)
        else:
            name = generate_customer_name()
        
        names.add(name)
        attempts += 1
    
    return list(names)
