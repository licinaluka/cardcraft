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
        ]
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
                ["script", """

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
                """]
            ],
        ],
        etype="html5",
        dir="ltr",
    )
