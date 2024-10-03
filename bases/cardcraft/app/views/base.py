import re

from flask import url_for
from pyhiccup.core import html

from cardcraft.app.views.theme import theme
from cardcraft.app.views.navigation import menu, navigation

js = lambda e: url_for("static", filename=e)


def trident(a, b, c):
    return [
        "div",
        {"class": "millers columns"},
        [
            ["div", {"class": "column primary", "id": "menu"}, a],
            ["div", {"class": "column secondary"}, b],
            ["div", {"class": "column tertiary"}, c],
        ],
    ]


async def hiccpage(page):
    return html(
        [
            [
                "head",
                [
                    "meta",
                    {
                        "content": "width=device-width, initial-scale=1",
                        "name": "viewport",
                    },
                ],
                ["meta", {"charset": "UTF-8"}],
                [
                    "link",
                    {
                        "rel": "stylesheet",
                        "href": "https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css",
                    },
                ],
                [
                    "link",
                    {
                        "rel": "stylesheet",
                        "href": "https://fonts.googleapis.com/icon?family=Material+Icons",
                    },
                ],
                ["style", {"type": "text/css"}, theme()],
            ],
            [
                "body",
                {"hx-boost": "true"},
                await navigation(),
                page,
                ["script", {"src": js("app/htmx.min.js")}, " "],
                ["script", {"src": js("app/json-enc.js")}, " "],
                ["script", "htmx.config.withCredentials=true"],
                ["script", {"src": js("app/bundle.js"), "type": "module"}, " "],
                [
                    "script",
                    """

                    /** */
                    async function move(e) {
                        console.log(e.target.className)
                        if (['card-render', 'c-title', 'c-image', 'c-content'].some(klass => e.target.className.includes(klass))) {
                            return false;
                        }

                        for (let el of document.querySelectorAll('.movable')) {
                            e.dataTransfer = new DataTransfer()
                            e.dataTransfer.setData('text', el.id)
                            el.classList.toggle('movable')
                            await drop(e)
                        }
                    }

                    /** */
                    async function drop(e) {
                        e.preventDefault()

                        if (! e.target.className.includes('spot')) {
                            let msg = 'Cards must be moved to "spots"!'
                            alert(msg)
                            throw msg
                        }

                        let id = e.dataTransfer.getData('text')
                        let card_id = id.replace('card-', '')

                        let el = document.querySelector('#' + id)
                        let hasCardAlready = 0 < e.target.querySelectorAll('.card-render').length
                        let row = (1 * e.target.parentNode.id.split('-')[1])
                        let isOpponentCard = row < 3 || e.target.parentNode.id.includes("unit-")
                        
                        let event = `player plays card ${card_id} to field position ${e.target.parentNode.id}`

                        if (hasCardAlready) {
                            let target = e.target.parentNode.id
                            if (target) {
                                event = `player uses ${card_id} to buff ${target}`
                            }
                        }

                        if (hasCardAlready && isOpponentCard) {
                            let target = e.target.parentNode.id
                            if (target) {
                                event = `player uses ${card_id} to attack ${target}`
                            }
                        }

                        e.target.appendChild(el)

                        await fetch(
                            `/web/part/game/matches/current/do`,
                            {
                                method: 'POST',
                                credentials: 'include',
                                body: JSON.stringify({'event': ['$me', event, null]}),
                                headers: {'Content-Type': 'application/json'}
                            }
                        )
                    }

                    /** */
                    function allowDrop(e) {
                        e.preventDefault()
                    }

                    /** */
                    document.onmousedown = (e) => {
                        setTimeout(() => {
                            if (! ['card-render', 'c-title', 'c-image', 'c-content'].some(klass => e.target.className.includes(klass))) {
                                return
                            }

                            if (window.holding) {
                                let card = e.target.closest('.card-render').cloneNode(true)
                                card.id = 'popup-card'
                                card.style.position = 'fixed';
                                card.style.top = '2em'
                                card.style.right = '2em'
                                document.querySelector('.game').append(card)
                            }

                            window.holding = e.target.closest('.card-render')
                        }, 1000)
                    }

                    /** */
                    document.onmouseup = (e) => {
                        window.holding = null
                        let card = document.querySelector('#popup-card')

                        if (card) {
                            card.parentNode.removeChild(card)
                        }
                    }
                """,
                ],
            ],
        ],
        etype="html5",
        dir="ltr",
    )


def landing():
    return [
        [
            "head",
            ["title", "Cardcraft, the Solana TCG builder"],
            [
                "link",
                {
                    "rel": "stylesheet",
                    "href": "https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css",
                },
            ],
            [
                "style",
                """
                body {
                    background-color: #000;
                    color: #fff;
                }
                a {
                    color: #9b59b6;
                }
                """,
            ],
        ],
        [
            "body",
            [
                [
                    "pre",
                    {"style": "white-space:break-spaces;"},
                    [
                        [
                            "span",
                            """
    # Project Leo
                                                                                                                                                                  
    cardcraft as a working title.
                                                                                                                                                                  
    A white-label Solana trading card game builder as a service (TCGBaaS) platform that helps trading card game designers on Solana solve - at least - problems of
                                                                                                                                                                  
    - game implementation details
    - content customization
    - gameplay customization
    - software development and distribution
                                                                                                                                                                  
    Why this project?
                                                                                                                                                                  
    Because if making a highly customizable card game engine was simple or easy, everyone would do it.
    But it's not simple, or easy, unless you have some tricks up your sleeve.
                                                                                                                                                                  
    """,
                        ],
                        [
                            "a",
                            {"href": "/home", "class": "btn purple"},
                            "Get started",
                        ],
                        [
                            "span",
                            """
    ---
    ## Project roadmap
                                                                                                                                                                  
    ### Eparistera Daimones
                                                                                                                                                                  
    Done so far (Oct 1st 2024):
        - wallet auth
        - highly customizable, human readable, card creation system
        - a human readable card API system
        - deck building
        - match listing & starting
        - match pot & payout
        - match pot can be funded by bot/system (play to earn)
        - a (very) basic opponent bot
        - minimal game *engine*
        - highly customizable game *rule system*
        - deployment automation
                                                                                                                                                                  
    ### The Starway Eternal
                                                                                                                                                                  
    Currently doing (TBA):
        - game engine features present in most card games
                                                                                                                                                                  
    ### Endorama
                                                                                                                                                                  
    Next steps (TBA):
        - playtest automation
        - match browser, match lobbies, tournaments
        - leaderboards and ranking systems
        - card ownership
        - card trading and renting
                                                                                                                                                                  
    ### Récidive
                                                                                                                                                                  
    Future steps:
        - multiple different white-label game clients (desktop/mobile etc)
        - match betting
        - authenticity/nonce verification for real, printed cards
        - producing real, printed cards
                                                                                                                                                                  
    """,
                        ],
                    ],
                ]
            ],
        ],
    ]


def faq():

    data: dict = {
        "What is this project?": "A white-label Solana trading card game builder. This instance (at https://cardcraft.ix.tc) is a demo.",
        "How do I use the demo?": "Create cards in the <a class='purple-text lighten-2' href='/cards'>card creator</a>, add them to your decks in the <a class='purple-text lighten-2' href='/decks'>deck builder</a>, then <a class='purple-text lighten-2' href='/home'>play a match</a> using one of your decks",
        "What is a white-label Solana trading card game builder?": "A turnkey software solution that helps you build a highly custom trading card game you've always been wanting to build.",
        "What are the key features of this project?": "At the moment, wallet sign in, flexible card creation, a deck builder, playing a match for SOL and a rudimentary game engine, game screen, and opponent bot.",
        "How can I make my own game?": "Install via ssh: <br /><pre>ssh you@yourvps.com -f 'wget https://raw.githubusercontent.com/licinaluka/cardcraft/refs/heads/master/config/deploy.sh | sh -'</pre>",
        "Why use this instead of programming my own?": "The overhead. <br /> <br /> In a scenario where you want to make a game but let someone else worry about the software, while we want to write the software and let someone else worry about game balancing and worldbuilding, we have a win-win situation.",
        "What types of card games can be built using this?": "The secret ingredient in this project is a highly flexible rule engine, card events we can support are basically limitless. Current game engine - though - is limited to 1 on 1 gameplay without a resource system.",
        "What kind of customization options are available for game creators?": "For MVP, you can configure bot pot behavior, pot payouts. First steps towards customizing look and feel for the web version will be in the form of minimal CMS functionality with a few pre-installed theme variations into which you can put your own branding.",
        "What kind of support is available for creators?": "We will provide automatic updates in an approach similar to the installation script, and prioritized custom patches on demand. We will also assist and advise programmers on implementing their own features.",
        "What are the pricing and licensing plans?": "TBA",
        "What is the roadmap for development?": "<ul><li>'The Starway Eternal' (TBA)</li><p>implementing features present in most card games; <li>'Endorama' (TBA)</li> <p>playtest automation, match browser, lobbies, tournaments, leadership, ranking system, card ownership, trading and renting;</p> <li>Récidive (TBA) </li> <p>multiple game clients, match betting, nonce verification for real, printed cards</p></ul>",
        "Any plans to integrate with other Solana projects": "TBA",
        "Any plans to integrate with other non-blockchain and blockchain software?": "TBA",
        "What are the plans for monetization and revenue generation?": "TBA",
        "What separates this project from other similar projects?": "The secret ingredient, the flexible rule engine.",
    }

    slug = lambda e: re.sub(r"[\W_]+", "-", e).lower().strip("-")

    return (
        [
            "ul",
            {"class": "collection"},
            [
                [
                    "li",
                    {"class": "collection-item"},
                    [
                        "a",
                        {
                            "href": f"#{slug(q)}",
                            "onclick": "document.querySelector('#faq').classList.toggle('game')",
                        },
                        f"{i+1}. {q}",
                    ],
                ]
                for i, (q, a) in enumerate(data.items())
            ],
        ],
        [
            [
                "div",
                {"class": "floater"},
                [
                    "a",
                    {
                        "class": "material-icons",
                        "href": "#",
                        "onclick": "document.querySelector('#faq').classList.toggle('game')",
                    },
                    "close",
                ],
            ],
            [
                "div",
                {"id": "faq", "class": ""},
                [
                    [
                        [
                            [
                                "h5",
                                {"id": slug(q)},
                                ["a", {"href": f"#{slug(q)}"}, f"{i+1}. {q}"],
                            ],
                            ["p", a],
                            ["br"],
                        ]
                        for i, (q, a) in enumerate(data.items())
                    ]
                ],
            ],
        ],
    )
