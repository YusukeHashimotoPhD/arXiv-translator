import arxiv
import streamlit as st
import deepl
import pandas as pd

st.set_page_config(layout="wide")


@st.cache
def load_data(query, sort_by_text):
    #    sort_by_text = 'Last updated date'
    dict_sort_by = {'Last updated date': arxiv.SortCriterion.LastUpdatedDate,
                    'Submitted date': arxiv.SortCriterion.SubmittedDate, 'Relevance': arxiv.SortCriterion.Relevance}
    sort_by = dict_sort_by[sort_by_text]
    search = arxiv.Search(
        query=query,
        max_results=100,
        sort_by=sort_by
    )

    df = pd.DataFrame()

    for result in search.results():
        index = result.published
        df.loc[index, 'title'] = result.title
        df.loc[index, 'published'] = result.published
        df.loc[index, 'updated'] = result.updated
        authors = result.authors
        df.loc[index, 'authors'] = ', '.join([str(author) for author in authors])
        df.loc[index, 'summary'] = result.summary
        categories = result.categories
        df.loc[index, 'category'] = ', '.join([str(category) for category in categories])
        df.loc[index, 'doi'] = result.doi
        df.loc[index, 'journal'] = result.journal_ref
        df.loc[index, 'pdf_url'] = result.pdf_url
        df.loc[index, 'comment'] = result.comment
        links = result.links
        df.loc[index, 'link'] = ', '.join([str(link) for link in links])

#    df['updated'] = pd.to_datetime(df['updated'])
#    df['published'] = pd.to_datetime(df['published'])

    # if sort_by_text == 'Last updated date':
    #     df['date'] = df['updated'].dt.date
    # else:
    #     df['date'] = df['published'].dt.date

    return df


# @st.cache
def authorize_to_deepl(auth_key):
    return deepl.Translator(auth_key)


@st.cache
def translate_text(translator, text, lang):
    return translator.translate_text(text, target_lang=lang)


@st.cache
def load_division_data():
    file_path = './data/major_class.csv'
    df_major = pd.read_csv(file_path, index_col=1)
    file_path = './data/minor_class.csv'
    df_minor = pd.read_csv(file_path, index_col=1)
    return df_major, df_minor


df_major, df_minor = load_division_data()
df = pd.DataFrame()
#dict_language = {'Japanese': 'JA', 'German': 'DE', 'French': 'FR', 'Italian': 'IT', 'Spanish': 'ES', 'Dutch': 'NL',
#                 'Polish': 'PL'}
dict_language = {'Bulgarian':'BG', 'Czech':'CS', 'Danish':'DA', 'German':'DE', 'Greek':'EL', 'English':'EN', 'Spanish':'ES', 'Estonian':'ET', 'Finnish':'FI', 'French':'FR', 'Hungarian':'HU', 'Indonesian':'ID', 'Italian':'IT', 'Japanese':'JA', 'Lithuanian':'LT', 'Latvian':'LV', 'Dutch':'NL', 'Polish':'PL', 'Portuguese':'PT', 'Romanian':'RO', 'Russian':'RU', 'Slovak':'SK', 'Slovenian':'SL', 'Swedish':'SV', 'Turkish':'TR', 'Ukrainian':'UK', 'Chinese':'ZH'}

auth_key = st.text_input('Please enter your auth_key for the DeepL api')

sort_by_text = st.selectbox(
    'Sort by',
    ['Last updated date', 'Submitted date'],
    index=0
)

st.write('Filter')

col1, col2 = st.columns(2)

with col1:
    filter_journal = st.checkbox(
        'Published'
    )

with col2:
    filter_accepted = st.checkbox(
        'Accepted'
    )

col1_A, col2_A, = st.columns(2)
with col1_A:
    list_major = ['-- Please select --'] + list(df_major.index)
    major_division = st.selectbox(
        'Major division',
        list_major,
        index=0
    )

    if major_division != list_major[0]:
        code_major = df_major.loc[major_division, 'code_major']
        df_minor_selected = df_minor[df_minor['code_minor'].str.contains(code_major)]
        list_minor = df_minor_selected.index
    else:
        list_minor = list_major[0]

    with col2_A:
        minor_division = st.selectbox(
            'Minor division',
            list_minor,
            disabled=(major_division == list_major[0]),
            index=0
        )

search_keyword = st.text_input(
    'Search keyword'
)

if (len(minor_division) != 1) | (len(search_keyword) != 0):
    if len(minor_division) != 1:
        code_minor = df_minor.loc[minor_division, 'code_minor']
    else:
        code_minor = ''

    if len(search_keyword) != 0:
        list_text = search_keyword.split(' ')
        if len(list_text) == 1:
            combined_text = search_keyword
        else:
            combined_text = ' AND '.join(list_text)
    else:
        combined_text = ''

    if len(search_keyword) != 0:
        if len(minor_division) != 1:
            query = f'cat:{code_minor} AND ' + combined_text
        else:
            query = combined_text
    else:
        if len(minor_division) != 1:
            query = f'cat:{code_minor}'
        else:
            query = ''

    df = load_data(query, sort_by_text)

    if filter_journal:
        df = df.dropna(subset=['journal'])

    if filter_accepted:
        df = df.dropna(subset=['comment'])
        df = df[df['comment'].str.contains('Accepted')]

if len(df) != 0:
    translate = False

    if auth_key != '':
        translator = authorize_to_deepl(auth_key)
        usage = translator.get_usage()

        select_language = st.selectbox(
            'Language',
            list(dict_language.keys()),
            disabled=(auth_key == ''),
            index=13
        )

        lang = dict_language[select_language]

        if usage.character.limit_reached:
            st.write("Character limit reached.")
        else:
            st.write(f"Character usage: {usage.character}")
            st.progress(usage.character.count / usage.character.limit)

    page_num = st.number_input(
        'Page of ' + str(len(df)),
        min_value=1,
        max_value=len(df)
    )
    index = df.index[page_num - 1]

    title = df.loc[index, 'title'].replace('\n', ' ')
    st.subheader(title)
    if translate:
        st.write(translate_text(translator, title, lang))

    st.caption(df.loc[index, 'authors'])

    updated_datetime = df.loc[index, 'updated'].strftime('%Y-%m-%d')
    published_datetime = df.loc[index, 'published'].strftime('%Y-%m-%d')
    if updated_datetime == published_datetime:
        dateLabel = f'Published: {published_datetime}'
    else:
        dateLabel = f'Published: {published_datetime}, Updated: {updated_datetime}'
    st.write(dateLabel)

    summary = df.loc[index, 'summary'].replace('\n', ' ')
    st.write(summary)
    if translate:
        st.write(translate_text(translator, summary, lang))

    journal_str = str(df.loc[index, 'journal'])
    if journal_str != 'None':
        if journal_str != 'nan':
            st.caption(journal_str)

    st.caption(df.loc[index, 'pdf_url'])

    doi_text = str(df.loc[index, 'doi'])
    if doi_text != 'None':
        if doi_text != 'nan':
            st.caption(doi_text)

    if str(df.loc[index, 'comment']) != 'None':
        st.caption(df.loc[index, 'comment'])

    if auth_key != '':

        word_counts = len(df.loc[index, 'title']) + len(df.loc[index, 'summary'])

        translate = st.checkbox(f'Translate? ({word_counts} characters)',
                                disabled=(auth_key == '')
                                )

    if translate:
        st.subheader(translate_text(translator, title, lang))
        st.write(translate_text(translator, summary, lang))

else:
    if (len(minor_division) != 1) | (len(search_keyword) != 0):
        st.title('No result was obtained!')
        st.subheader('Please change division or search keyword.')
    else:
        st.title('Welcome to arXiv translator!')
        st.subheader('How to use?')
        st.write(
            'Please choose the major and minor divisions of the research fields you want to investigate. Then, '
            'you will see information of papers submitted to arXiv. Search keyword can be given.')
        st.write(
            'Published and accepted filters select the manuscript with url of publisher and "Acceptted" in the comment, respectively.')
        st.write(
            'If you want to translate the documents, please paste API key from your DeepL account obtained in '
            'https://www.deepl.com/en/pro/change-plan#developer. Then, check the checkbox of left side of "translate?". '
            'You will see the translated documents.')
        st.write(
            'Note that, if you use the free version of the deepL api, the translation word is limited to 500,'
            '000, which corresponds to roughly 500 pages, per month.')
        st.write(
        'We will not take any responsibility for any loss, damage, or troubles that may be caused by using this system.')