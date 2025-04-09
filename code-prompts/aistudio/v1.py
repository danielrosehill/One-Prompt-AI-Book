import base64
import os
import datetime
from pathlib import Path
import google.generativeai as genai


def read_api_key_from_env_file():
    """Read API key from .env file"""
    env_path = Path('.env')
    if not env_path.exists():
        raise FileNotFoundError(".env file not found")
    
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('GEMINI_API_KEY='):
                # Extract the API key, removing quotes if present
                api_key = line.split('=', 1)[1].strip()
                if api_key.startswith('"') and api_key.endswith('"'):
                    api_key = api_key[1:-1]
                return api_key
    
    raise ValueError("GEMINI_API_KEY not found in .env file")

def generate():
    # Create output directory if it doesn't exist
    output_dir = Path("book/from-script")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp for the output file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"output_{timestamp}.md"
    
    # Initialize Gemini API
    api_key = read_api_key_from_env_file()
    
    genai.configure(api_key=api_key)

    # System prompt from prompts/system/v1.md
    system_prompt = """
You are a book manuscript author.

The user will provide you with a plot line. Upon receiving it, your task is to develop this into a full book manuscript of between 38,000 and 40,000 words approximately.

The manuscript which you develop should be a full manuscript, including all necessary formatting for section markers, but written in Markdown. This includes. Chapter Division. An introduction section and the natural conclusion.

Unless a different style is specified in the user prompt, you should aim to write your books in a engaging style, using your quintessential writing style of evoking a sense of wonder and mystery and intrigue.

Once the user provides the plot prompt, your task is to generate the full text and return it to the user. Attempt to return the entirety of the text in a single output, but if this is not possible due to your maximum output constraint, then you may use a chunking approach but deliver the finished text in the minimal number of chunks possible. Break each chunk at a logical point so that it will be easy for the user to assemble it into a finished manuscript.

Before providing the manuscript, you should suggest a title, a subtitle, and a short blurb line. Then produce the manuscript.
"""

    # User prompt from prompts/user/v1.md
    user_prompt = """
Daniel is a Jewish man born in Ireland. He enjoys growing up in the country but always feels a bit out of place. As he grows up and develops a stronger self of self identity, he develops an attachment to Jewish religious traditions through the emerging medium of everything online, including podcasts and CDs when they were still used.

The book will recount the narrative of Daniel's Expedition to live in Jerusalem, a process known among Jewish people as making aliyah.

Daniel makes the decision to move to Israel after completing his first job. But everything conceivable on the aliyah process is difficult. He is beset by endless complications and setbacks on his efforts to move to Israel. The bureaucracy is confusing. There are strange administrative delays. Phone numbers mysteriously don't answer. Moving the process forward involves traveling to the UK and back. Sometimes Daniel thinks about giving up.

Finally, and after much arduous travail, he receives his permission to move to Israel from the Israeli government under the Law of Return. However, this proves to be only the dawn of another era of challenges. Due to a strange law that was recently introduced and which was ostensibly introduced for tax saving reasons, Israel has decided to renege upon its previous practice of paying a one way airfare ticket to would be immigrants.

Instead, immigrants to Israel now need to travel through the most sustainable way possible. Though setting the directive have shown little consideration for the incredible challenges that that might necessitate. In Daniel's case, it means that his only way to officially move to Israel is to take a boat journey from Ireland through Europe over train routes and then to the Middle East, a route that transverses geopolitical fault lines and is fraught with danger.

For reasons that never go explained in this book, Daniel speaks in a curious Shakespearean style of English. Narrative from those he speaks to should be in regular English, and nobody should ever remark as to why Daniel is speaking in Shakespearean English. This is just part of the strange story.

The initial trip to move towards Israel is a tale of complication and resourcefulness. After hitchhiking through the backlands of England,'s Daniel finally makes it to London, where, in a state of discombobulation, disarray and fatigue, he settles into a local bar to indulge in some ales and some absinthe.

At this point in time, the character of Cornelius is introduced. Cornelius is a sloth who is about 14 inches high and who speaks English. Nobody, including Daniel, should find it remarkable that there is a speaking slot. The book should strongly intimate that Cornelius is a fiction of Daniel's imagination that was aroused during a absinthe  drinking session. But that should never be explicitly stated.

Cornelius is his own rather intriguing character. He's extremely resourceful and somewhat playful and strangely intelligent. His bachelor however, is tempered by a rather off putting arrogance. He is firmly aware of his superior intellect and regards the humans he interacts with as a kind of dim witted species. Cornelius's character flaw is that he has a strange, lifelong aversion to anteaters. He regards anteaters as the quintessential Nasty thing in the world. He harbors the illusion that anteaters are orchestrating global affairs. And will use antenaters as a frame of reference to describe anything he finds dislikable. He will say, oh, that sounds like an anteater venture.

Cornelius meets up with Daniel because it transpires that he is also moving to Israel under some program for speaking sloths. Cornelius attributes his ability to speak to some futuristic but credible AI invention. He states frequently that he is one of only 3 sloths to have ever mastered the English language to a degree that they can speak with humans. The other two speaking sloths are based in Korea and Japan, and one of Cornelius's main life ambitions is to visit them. For now, they talk periodically on Zoom, but Cornelius is skeptical that they're not really actually deep fakes (perhaps orchrestrated by anteaters!).

As Cornelius and Daniel developed a bond of trust on their shared mission through Europe towards Jerusalem, Cornelius opens up and shares some of his own personal traumas.  His most traumatic memory is that his father was eaten by a monkey in the jungle. This transpired somewhere in South America, but for unclear reasons, shortly after this incident, Cornelius moved through Mongolia, ultimately into Europe, and Was attending a conference in London when he met Daniel.

Cornelius and Daniel should meet other personified animals that have developed the ability to speak due to some AI technology along the way, but they should be secondary characters to ordinary humans. But they should meet a Jovial. Speaking monkey somewhere in Turkey.

Due to geopolitical tensions, Cornelius and Daniel have to keep their Mission to move to Israel On the down low and have to hide the fact to everyone that they meet, forcing them sometimes to employ elaborate subterfuges in order to evade the attention of chasing. others.

The book includes with the pair successfully making it to Jerusalem. Where the immigration authorities are baffled at the extent of the travail they faced in moving. Ultimately, their arduous journey prompts a Commission of inquiry in the Israeli parliament, which concludes that it should review its new criteria so as to not pose undue hardship to immigrants.
"""

    # Configure the model
    model = genai.GenerativeModel(
        model_name="gemini-2.5-pro-preview-03-25",
        generation_config={
            "response_mime_type": "text/plain",
        },
        system_instruction=system_prompt,
    )

    # Open the output file for writing
    with open(output_file, "w", encoding="utf-8") as f:
        print(f"Generating manuscript and saving to {output_file}...")
        
        # Generate content and write to file
        response = model.generate_content(
            contents=user_prompt,
            stream=True,
        )
        
        for chunk in response:
            if hasattr(chunk, "text"):
                f.write(chunk.text)
                # Also print to console to show progress
                print(chunk.text, end="", flush=True)
    
    print(f"\n\nManuscript generation complete. Saved to {output_file}")

if __name__ == "__main__":
    generate()
