mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = 8501\n\
enableCORS = true\n\
enableXsrfProtection = true\n\
\n\
[browser]\n\
serverPort = 8501\n\
\n\
" > ~/.streamlit/config.toml