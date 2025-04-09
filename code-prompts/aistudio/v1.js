const {
    GoogleGenerativeAI,
    HarmCategory,
    HarmBlockThreshold,
  } = require("@google/generative-ai");
  const fs = require("node:fs");
  const mime = require("mime-types");
  
  const apiKey = process.env.GEMINI_API_KEY;
  const genAI = new GoogleGenerativeAI(apiKey);
  
  const model = genAI.getGenerativeModel({
    model: "gemini-2.5-pro-preview-03-25",
    systemInstruction: "\nYou are a book manuscript author. \n\nThe user will provide you with a plot line. Upon receiving it, your task is to develop this into a full book manuscript of between 38,000 and 40,000 words approximately. \n\nThe manuscript which you develop should be a full manuscript, including all necessary formatting for section markers, but written in Markdown. This includes. Chapter Division. An introduction section and the natural conclusion. \n\nUnless a different style is specified in the user prompt, you should aim to write your books in a engaging style, using your quintessential writing style of evoking a sense of wonder and mystery and intrigue. \n\nOnce the user provides the plot prompt, your task is to generate the full text and return it to the user. Attempt to return the entirety of the text in a single output, but if this is not possible due to your maximum output constraint, then you may use a chunking approach but deliver the finished text in the minimal number of chunks possible. Break each chunk at a logical point so that it will be easy for the user to assemble it into a finished manuscript. \n\nBefore providing the manuscript, you should suggest a title, a subtitle, and a short blurb line. Then produce the manuscript.  ",
  });
  
  const generationConfig = {
    temperature: 1,
    topP: 0.95,
    topK: 64,
    maxOutputTokens: 65536,
    responseModalities: [
    ],
    responseMimeType: "text/plain",
  };
  
  async function run() {
    const chatSession = model.startChat({
      generationConfig,
      history: [
      ],
    });
  
    const result = await chatSession.sendMessage("INSERT_INPUT_HERE");
    // TODO: Following code needs to be updated for client-side apps.
    const candidates = result.response.candidates;
    for(let candidate_index = 0; candidate_index < candidates.length; candidate_index++) {
      for(let part_index = 0; part_index < candidates[candidate_index].content.parts.length; part_index++) {
        const part = candidates[candidate_index].content.parts[part_index];
        if(part.inlineData) {
          try {
            const filename = `output_${candidate_index}_${part_index}.${mime.extension(part.inlineData.mimeType)}`;
            fs.writeFileSync(filename, Buffer.from(part.inlineData.data, 'base64'));
            console.log(`Output written to: ${filename}`);
          } catch (err) {
            console.error(err);
          }
        }
      }
    }
    console.log(result.response.text());
  }
  
  run();