mkdir -p ~/.streamlit/
echo "\
[global]\n\
dataFrameSerialization=\"Legacy\"\n\
\n\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
enableXsrfProtection = false\n\
\n\
" > ~/.streamlit/config.toml