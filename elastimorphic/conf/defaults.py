ES_URLS = ["http://localhost:9200"]

ES_SETTINGS = {
    "index": {
        "analysis": {
            "analyzer": {
                "autocomplete": {
                    "type": "custom",
                    "char_filter": ["quotes"],
                    "tokenizer": "edge_ngram_tokenizer",
                    "filter": ["asciifolding", "lowercase"]
                },
                "html": {
                    "type": "custom",
                    "char_filter": ["html_strip", "quotes"],
                    "tokenizer": "standard",
                    "filter": ["asciifolding", "lowercase", "stop", "snowball"]
                }
            },
            "char_filter": {
                "quotes": {
                    "mappings": [
                        "\u0091=>\u0027",
                        "\u0092=>\u0027",
                        "\u2018=>\u0027",
                        "\u2019=>\u0027",
                        "\uFF07=>\u0027"
                    ],
                    "type": "mapping"
                },
            },
            "tokenizer": {
                "edge_ngram_tokenizer": {
                    "type": "edgeNGram",
                    "min_gram": "3",
                    "max_gram": "10",
                    "token_chars": "letter"
                }
            }
        }
    }
}
