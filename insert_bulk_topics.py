import sqlite3
from datetime import datetime

DB_PATH = 'data/bot.db'

def insert_bulk_topics():
    from utils import db
    db.init()
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_topics = [
        # IELTS PART 1
        (1, "ALL", "IELTS", "Let's talk about your hometown. Where is your hometown? What is it like? Is it a good place to live?", "Hometown"),
        (1, "ALL", "IELTS", "Let's talk about your studies/work. Do you work or are you a student? What do you like about your job/studies?", "Work/Study"),
        (1, "ALL", "IELTS", "Do you like reading? What kind of books do you read? Did you read much as a child?", "Reading"),
        (1, "ALL", "IELTS", "Let's talk about music. What kind of music do you like listening to? Have you ever learned to play a musical instrument?", "Music"),
        (1, "ALL", "IELTS", "Do you often use public transport? How do you usually travel around your city? What's the best way to travel?", "Transport"),
        (1, "ALL", "IELTS", "Let's talk about weather. What's the weather like in your country? Do you prefer hot or cold weather?", "Weather"),
        (1, "ALL", "IELTS", "Do you like cooking? How often do you cook? What is your favorite dish to prepare?", "Food"),
        (1, "ALL", "IELTS", "Let's talk about sports. Do you play any sports? What sports are popular in your country?", "Sports"),
        (1, "ALL", "IELTS", "Do you have any pets? Did you have a pet when you were a child? Why do people keep pets?", "Pets"),
        (1, "ALL", "IELTS", "Let's talk about shopping. Do you enjoy shopping? Do you prefer shopping online or in stores?", "Shopping"),
        (1, "ALL", "IELTS", "How do you usually spend your weekends? Are your weekends different now compared to when you were a child?", "Weekends"),
        (1, "ALL", "IELTS", "Let's talk about art. Do you like art? Have you ever visited an art gallery? Is art popular in your country?", "Art"),
        (1, "ALL", "IELTS", "What is your favorite color? Has your favorite color changed since you were a child? What color would you never paint your room?", "Colors"),
        (1, "ALL", "IELTS", "Let's talk about daily routine. What is your typical morning routine? Is your routine different on weekends?", "Daily Routine"),
        (1, "ALL", "IELTS", "Do you like taking photographs? What do you usually take photos of? Do you prefer to use a camera or your phone?", "Photography"),

        # IELTS PART 2
        (2, "ALL", "IELTS", "Describe a book you have recently read.\n• What the book is\n• Who wrote it\n• What it is about\n• Why you decided to read it", "Books"),
        (2, "ALL", "IELTS", "Describe a place you have visited that you would recommend to others.\n• Where it is\n• How you traveled there\n• What you did there\n• Why you would recommend it", "Travel"),
        (2, "ALL", "IELTS", "Describe a successful small company or business that you know.\n• What the business is\n• How you know about it\n• Who its customers are\n• Why you think it is successful", "Business"),
        (2, "ALL", "IELTS", "Describe an interesting conversation you had with a stranger.\n• Who the person was\n• Where you met them\n• What you talked about\n• Why you found the conversation interesting", "People"),
        (2, "ALL", "IELTS", "Describe a time when you helped someone.\n• Who you helped\n• How you helped them\n• Why you helped them\n• How you felt after helping them", "Experience"),
        (2, "ALL", "IELTS", "Describe a useful piece of equipment that you use at home.\n• What it is\n• How often you use it\n• How it works\n• Why it is so useful to you", "Technology"),
        (2, "ALL", "IELTS", "Describe an important historical event in your country.\n• What the event was\n• When it happened\n• Who was involved\n• Why it is considered important", "History"),
        (2, "ALL", "IELTS", "Describe a piece of good advice you recently received.\n• What the advice was\n• Who gave it to you\n• When you received it\n• Why it was helpful to you", "Advice"),
        (2, "ALL", "IELTS", "Describe a film you watched recently that you enjoyed.\n• What the film was\n• Who you watched it with\n• What it was about\n• Why you enjoyed it", "Movies"),
        (2, "ALL", "IELTS", "Describe a park or garden in your city that you like visiting.\n• Where it is\n• What it looks like\n• What people do there\n• Why you like visiting it", "Places"),

        # IELTS PART 3
        (3, "ALL", "IELTS", "Why do some people prefer reading physical books rather than e-books? How has the internet changed the way people read?", "Books & Media"),
        (3, "ALL", "IELTS", "What are the advantages and disadvantages of tourism for a country? How does travel change people's perspectives?", "Travel & Society"),
        (3, "ALL", "IELTS", "What qualities make a business successful? Do you think big corporations have too much power nowadays?", "Business & Economy"),
        (3, "ALL", "IELTS", "Why is it important to communicate with people from different backgrounds? How has social media changed how we interact with strangers?", "Communication"),
        (3, "ALL", "IELTS", "Why should people do volunteer work? Do you think society is becoming more selfish or more helpful?", "Society"),
        (3, "ALL", "IELTS", "How has technology changed family life? What are the negative impacts of relying too much on machines at home?", "Technology"),
        (3, "ALL", "IELTS", "Why should children learn history in school? How can museums make history more interesting for young people?", "History & Education"),
        (3, "ALL", "IELTS", "Whose advice do young people usually follow: their parents' or their friends'? Why is it sometimes hard to accept advice?", "Advice & Relationships"),
        (3, "ALL", "IELTS", "Do you think films have an educational value? How has the film industry changed over the last 20 years?", "Movies & Culture"),
        (3, "ALL", "IELTS", "Why is it important to have green spaces in cities? Should governments spend more money on public parks?", "Environment & Cities"),

        # CEFR MULTILEVEL PART 1
        (1, "ALL", "CEFR", "Tell me about your family. Do you have a large or small family? What do you usually do together?", "Family"),
        (1, "ALL", "CEFR", "What are your plans for the future? Where do you see yourself in 5 years? Why did you choose this path?", "Future Plans"),
        (1, "ALL", "CEFR", "How long have you been learning English? What do you find most difficult about learning languages?", "Education"),
        (1, "ALL", "CEFR", "Tell me about your favorite season. Why do you like it? What activities do you do during this season?", "Seasons"),
        (1, "ALL", "CEFR", "What is your favorite type of clothing? Do you prefer comfortable clothes or fashionable ones? Why?", "Clothing"),
        (1, "ALL", "CEFR", "Do you like watching the news? Where do you usually get your news from? Is it important to stay informed?", "News"),
        (1, "ALL", "CEFR", "Tell me about your neighborhood. What are the advantages and disadvantages of living there?", "Neighborhood"),
        (1, "ALL", "CEFR", "How do you manage your time? Do you use a planner or an app? Why is time management important?", "Time Management"),
        (1, "ALL", "CEFR", "Do you prefer studying alone or in a group? Why? What helps you concentrate better?", "Study Habits"),
        (1, "ALL", "CEFR", "Tell me about your best friend. How long have you known them? What makes your friendship strong?", "Friendship"),

        # CEFR MULTILEVEL PART 2
        (2, "ALL", "CEFR", "Tell me about a difficult challenge you have faced.\n• What the challenge was\n• When it happened\n• How you overcame it\n• What you learned from this experience", "Challenges"),
        (2, "ALL", "CEFR", "Describe a traditional festival or celebration in your country.\n• What the festival is\n• When it is celebrated\n• What people do during the festival\n• Why it is important to your culture", "Culture"),
        (2, "ALL", "CEFR", "Tell me about a time when you had to work in a team.\n• What the task was\n• Who was in your team\n• What your role was\n• Whether the team was successful or not", "Teamwork"),
        (2, "ALL", "CEFR", "Describe an interesting article you recently read on the internet.\n• What the article was about\n• Where you read it\n• Why you read it\n• Why you found it interesting", "Media"),
        (2, "ALL", "CEFR", "Tell me about a mistake you made and what you learned from it.\n• What the mistake was\n• When it happened\n• What the consequences were\n• How it changed your behavior", "Experience"),
        (2, "ALL", "CEFR", "Describe an important invention that you think has changed the world.\n• What the invention is\n• Who invented it (if you know)\n• How it works\n• Why it is so important", "Inventions"),
        (2, "ALL", "CEFR", "Tell me about a time when you experienced a significant change in your life.\n• What the change was\n• Why it happened\n• How you felt about it\n• How it affected your future", "Life Changes"),

        # CEFR MULTILEVEL PART 3
        (3, "ALL", "CEFR", "Some people believe that university education should be free for everyone. Others think students should pay.\nDiscuss both views and give your opinion.", "Education"),
        (3, "ALL", "CEFR", "In many countries, traditional customs are being lost as a result of globalization.\nWhat are the causes of this? Is it a positive or negative development?", "Culture & Globalization"),
        (3, "ALL", "CEFR", "Many people argue that the government should spend more money on healthcare than on space exploration.\nTo what extent do you agree or disagree?", "Government Spending"),
        (3, "ALL", "CEFR", "Some people think that strict punishments for driving offences are the only way to reduce traffic accidents.\nTo what extent do you agree or disagree?", "Crime & Punishment"),
        (3, "ALL", "CEFR", "With the rise of artificial intelligence, many human jobs might be replaced by machines.\nWhat are the advantages and disadvantages of this trend?", "Technology & Jobs"),
        (3, "ALL", "CEFR", "It is often said that advertising encourages people to buy things they do not really need.\nDo you agree or disagree? Support your answer with examples.", "Advertising"),
        (3, "ALL", "CEFR", "Some people prefer to live in a house, while others prefer living in an apartment.\nWhat are the pros and cons of each? Which do you prefer and why?", "Housing"),
        (3, "ALL", "CEFR", "Nowadays, children spend a lot of time playing computer games instead of participating in sports.\nWhat are the reasons for this? How can this issue be solved?", "Health & Lifestyle")
    ]
    
    count = 0
    for topic in new_topics:
        c.execute(
            "INSERT INTO topics (part, level, exam, topic, category, added_by, created_at) VALUES (?,?,?,?,?,?,?)",
            (topic[0], topic[1], topic[2], topic[3], topic[4], 1, date)
        )
        count += 1
        
    conn.commit()
    conn.close()
    print(f"Successfully inserted {count} MORE real topics into the database.")

if __name__ == '__main__':
    insert_bulk_topics()
