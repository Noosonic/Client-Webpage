mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = true\n\
enableXsrfProtection = true\n\
\n\
[browser]\n\
serverPort = $PORT\n\
\n\
" > ~/.streamlit/config.toml