# Converting scraped data to data structure using LLM's

## Creating the environment

Run the following code chunk to get started with the environment

```bash
> python -m venv newvenv
> source newvenv/bin/activate
> pip install -r requirements.txt
```

## API key

To store the API keys create a .env file in the base directory, and place the corresponding API keys. I have one from [together.ai](http://together.ai/) and another from [openAI](https://openai.com/blog/openai-api). Store them (as well as the url) in this file as shown below:

```
TOGETHERAI_API_KEY="<your api key>"
OPENAI_API_KEY="<your api key>"
URL="<your url>"
```

This will be loaded into the scripts while making the requests.

## Schema

The `src/schema.py` consists of custom schema defined as a wrapper on top of `BaseModel` provided by `pydantic`. This was done largely inspired by `instructor`'s implementation of function calling.

## Procedure and results

The url is scraped and the html is meaningfully extracted in`src/scrape.py`. As some additional sanitisation steps (and also to reduce prompt token size), some useless html tags such as `div`, `span`, `b` and some others were removed. More over, all style attributes were also removed from other tags (only rowspan attributes remain).

Finally each row of the table is extracted seperately and the entire table is converted into a list of html table rows. Then during passing the html input to the model query, each row is converted into string and append with two blank lines gap between each row. In prompt, a tip has been provided to nudge the model into focussing on which tags have a rowspan attribute as that will decide how many entries get the same movie name,

Demonstration of the results are in `html-to-json.ipynb`.

Now, since there are $\approx 50$ rows, passing the entire table as one input quickly runs out of token length limit. Hence I split the table into chunks of some fixed chunk length and appended the header row at the beginning of all of them. Then passed all of them as inputs in seperate queries and saved their JSON outputs. Finally I merged all the JSON outputs into one combined output. The outputs are the json files in the base directory.

## Other models

Somewhere from yesterday evening, most models I tried from together.ai endpoints returned http errors, and due to shortage of time I was unable to investigate this issue further (see [here](src/html-to-json.ipynb#trying-with-mistral-and-llama)). Hence I was forced to use the `gpt` models from OpenAI. 

