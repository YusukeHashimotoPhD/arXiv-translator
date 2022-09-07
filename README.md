# arXiv translator

This project aims to support non-native English researchers.
A web app. obtains information of papers submitted to arXiv through its api.
Then, the obtained documents are translated with deepL if you paste API key from your DeepL account.
 
To use this app, you can deploy this app by yourself with codes given in this repositly or use

https://yusukehashimotophd-arxiv-translator-main-agggx8.streamlitapp.com

for desktop or

https://yusukehashimotophd-arxiv-translator-main-agggx8.streamlitapp.com/For_cell_phone

for cell phone.

If you deploy by yourself, please prepare python enivronment and then install libraries by
<pre><code>pip install arXiv deepl pandas streamlit</code></pre>
and then run the 'main.py' code with streamlit by
<pre><code>streamlit run main.py</code></pre>
You may see the web app. in your web browser.


To translate the documents with deepL, please paste API key from your DeepL account obtained in https://www.deepl.com/en/pro/change-plan#developer.
If you use the free version of the deepL api, the translation words are limited to 500,000, which corresponds to roughly 500 pages, per month.

We will not take any responsibility for any loss, damage, or troubles that may be caused by using this system.
