import anthropic
import os
import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables and remove any quotes if present
api_key = os.getenv("ANTHROPIC_API_KEY")
if api_key:
    # Remove quotes if they exist
    api_key = api_key.strip('"\'')
    print("API key loaded successfully")
else:
    print("ERROR: API key not found in .env file")

# Initialize Anthropic client
client = anthropic.Anthropic(
    api_key=api_key,
)

# The prompt to send to Claude
prompt = "Here is the plot:\n\nDaniel is a Jewish man born in Ireland who enjoys his rural upbringing but often feels out of place. As he matures and develops a stronger sense of self-identity, he grows increasingly attached to Jewish religious traditions, largely through the emerging online mediums of podcasts and CDs.\n\nThis book narrates Daniel's expedition to live in Jerusalem, a process known among Jewish people as making aliyah.\n\nAfter completing his first job, Daniel decides to move to Israel. However, the aliyah process proves to be fraught with difficulties. He faces endless complications and setbacks, including confusing bureaucracy, strange administrative delays, and unanswered phone calls. Advancing his efforts requires traveling to the UK and back, and there are moments when he contemplates giving up.\n\nFinally, after much arduous effort, he receives permission from the Israeli government to move to Israel under the Law of Return. Yet this marks only the beginning of another set of challenges. Due to a newly introduced law, ostensibly for tax-saving purposes, Israel has stopped covering one-way airfare for would-be immigrants. Instead, newcomers must travel in the most sustainable way possible, a directive that shows little consideration for the incredible challenges it entails. For Daniel, this means that his only official route to Israel is by taking a boat journey from Ireland through Europe and into the Middle East—a path fraught with geopolitical tensions and danger.\n\nFor reasons unexplained in the book, Daniel speaks in a curious Shakespearean style of English. The dialogue of those he interacts with is in standard English, and nobody comments on Daniel's unique speech; it simply adds to the story's eccentricity.\n\nHis initial journey toward Israel is filled with complications and resourcefulness. After hitchhiking through the English countryside, Daniel finally arrives in London. There, in a state of confusion and fatigue, he settles into a local bar for some ales and absinthe.\n\nIt is at this point that Cornelius, a 14-inch tall sloth who can speak English, is introduced. No one—including Daniel—finds it remarkable that there is a talking sloth. The narrative strongly suggests that Cornelius is a figment of Daniel's imagination, inspired by his absinthe drinking session, but this is never explicitly stated.\n\nCornelius is an intriguing character—resourceful, playful, and surprisingly intelligent. However, he is also marked by an off-putting arrogance, viewing humans as somewhat dim-witted. He harbors a peculiar aversion to anteaters, whom he considers the epitome of unpleasantness and believes are secretly orchestrating global affairs. He often uses anteaters as a frame of reference to describe anything he dislikes, saying things like, \"Oh, that sounds like an anteater venture.\"\n\nCornelius meets Daniel because he, too, is moving to Israel under a program for speaking sloths. He claims that his ability to speak is due to some futuristic yet credible AI technology. Cornelius frequently mentions that he is one of only three sloths ever to have mastered English sufficiently to converse with humans. The other two speaking sloths reside in Korea and Japan, and one of Cornelius's main life ambitions is to visit them. For now, they communicate periodically via Zoom, though Cornelius is skeptical about whether they are real or just deep fakes—potentially orchestrated by anteaters!\n\nAs their bond grows during their shared mission through Europe toward Jerusalem, Cornelius opens up about his personal traumas. His most traumatic memory involves witnessing his father being eaten by a monkey in the jungle in South America. For unclear reasons, shortly after this incident, Cornelius traveled through Mongolia before arriving in Europe for a conference in London when he met Daniel.\n\nAlong their journey, Cornelius and Daniel encounter other personified animals who have gained the ability to speak through AI technology; however, these characters remain secondary to ordinary humans. They do meet a jovial speaking monkey somewhere in Turkey.\n\nDue to geopolitical tensions, Daniel and Cornelius must keep their mission to move to Israel under wraps, often employing elaborate subterfuges to evade the attention of those who might chase them.\n\nThe book concludes with Daniel and Cornelius successfully arriving in Jerusalem. The immigration authorities are baffled by the extent of their arduous journey. Ultimately, their experiences prompt a commission of inquiry in the Israeli parliament, which concludes that it needs to review its new criteria to avoid imposing undue hardship on immigrants."

# Create a timestamp for the output file
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
output_filename = "/home/daniel/Development/Repos/Gemini-2.5-Max-Output-Tokens-Test/code-prompts/anthropic/output_" + timestamp + ".md"

print("Sending request to Claude 3.7 Sonnet...")

# Send the request to Claude with streaming
with client.beta.messages.stream(
    model="claude-3-7-sonnet-20250219",
    max_tokens=128000,
    temperature=1,
    system="You are a book manuscript author. \n\nThe user will provide you with a plot line. Upon receiving it, your task is to develop this into a full book manuscript of between 38,000 and 40,000 words approximately. \n\nThe manuscript which you develop should be a full manuscript, including all necessary formatting for section markers, but written in Markdown. This includes. Chapter Division. An introduction section and the natural conclusion. \n\nUnless a different style is specified in the user prompt, you should aim to write your books in a engaging style, using your quintessential writing style of evoking a sense of wonder and mystery and intrigue. \n\nOnce the user provides the plot prompt, your task is to generate the full text and return it to the user. Attempt to return the entirety of the text in a single output, but if this is not possible due to your maximum output constraint, then you may use a chunking approach but deliver the finished text in the minimal number of chunks possible. Break each chunk at a logical point so that it will be easy for the user to assemble it into a finished manuscript. \n\nBefore providing the manuscript, you should suggest a title, a subtitle, and a short blurb line. Then produce the manuscript.  \n ",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }
    ],
    betas=["output-128k-2025-02-19"]
) as stream:
    # Initialize an empty string to collect all content
    full_response = ""
    
    # Open the output file for writing
    with open(output_filename, "w", encoding="utf-8") as f:
        # Print progress indicator
        print("Receiving response (this may take a while)...")
        
        # Process each message in the stream
        for text in stream.text_stream:
            # Append to our full response
            full_response += text
            # Write to file as we receive content
            f.write(text)
            # Print a dot to show progress
            print(".", end="", flush=True)

print("\nResponse saved to " + output_filename)

# Print a preview of the response (first 500 characters)
print("\nPreview of the response:")
print(full_response[:500] + "...")
