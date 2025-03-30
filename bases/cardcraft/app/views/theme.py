def theme():
    return """
.game {
  /* font-family: 'Perfect DOS VGA 437' !important; */
  font-size: initial;
}
                                                                      
body {
  scrollbar-color: #555 #222;
}
                                                                      
h1 {
  text-decoration: underline;
}
                                                                      
.columns {
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
}
.millers {
  overflow: hidden;
}
.column {
  flex-grow: 1;
  margin: 1em;
}
.column.primary {
  min-width: 16%;
}
.column.secondary {
  min-width: 32%;
  overflow: auto;
  height: 100vh;
}
.column.tertiary {
  min-width: 50%;
  overflow:auto;
  height: 100vh;
                                                                      
  scroll-behavior: smooth;
}
.column.secondary a[disabled=true] {
  pointer-events: none;
}

.blank {
  display: flex; justify-content: center; align-items: center; width: auto; height: 100vh
}

.game {
  padding: 2em;
  font-family: monospace;
}
.game *:hover {
  border-left: none;
}
.game *:target {
  /** background: #FBF719; */
  /** text-decoration: underline; */
  /** text-decoration-color: #673ab7; */
  padding-left: 0.2em;
  border-left: 2px solid #888;
}
.game > div {
  margin: 1em;
}
.game nav a {
  color: #111;
}
.game.web {
  height: 100vh;
}
                                                                      
a {
  color: inherit;
}

.item {
  background:inherit;
  color: inherit;
  padding: 1em;
  border-bottom: 1px solid;
}
                                                                      
.item[active=true] {
  text-decoration: underlined;
  font-weight: bold;
}
.floater {
  /** opacity: 0.4; */
  position: fixed;
  width: 1em;
}
.floater:hover {
  /** opacity: 0.9; */
}
::-webkit-scrollbar {
  width: 5px;
  height: 5px;
  /** display: none; */
}
::-webkit-scrollbar-track {
  background: #222;
}
::-webkit-scrollbar-thumb {
  background: #555;
}
pre {
  overflow-x: scroll;
  background: #222;
  color: #ddd;
                                                                      
  padding: 1em;
  font-size: 0.7em;
}
pre strong {
  white-space: pre;
}
strong {
  white-space: normal;
}
img {
  width: 100%;
  background: rgba(250, 250, 250, .5);
}
                                                                      
                                                                      
.game ul:not(.browser-default) {
  padding-left: revert;
}
.game ul:not(.browser-default)>li {
  list-style-type: initial;
}
                                                                      
.game ol:not(.browser-default) {
  padding-left: revert;
}
.game ol:not(.browser-default)>li {
  /* list-style-type: initial; */
}

.game .board {
  min-height: 100vh;
}

.game .board .opponent {
  display: flex;
  align-items: flex-start;  
}

.game .board .battle {
  display: flex;
  /* align-items: flex-middle; */
  min-height: 30%;
  flex-direction: column;
}

.game .board .hand {
  display: flex;
}

.game .board .hand .card-container {
  width: 1px;
  flex-grow: 1;
}

.game .board .hand .card-container:last-child {
  width: 100px;
  flex-grow: 0;
}

.game .board .field {
  display: flex;
}

.game .board .spot {
  padding: 1em;
  margin: 1em;
  width: 5em;
  height: 10em;
  border: 1px solid #555;
  overflow: auto;
}

.game .board .spot .card-render {
  width: 5em;
  height: 5em;
  overflow: hidden;
  padding: unset;
  margin: unset;
}

.game .board .spot .card-render * {
  visibility: hidden;
  height: 0px;
  margin: 0px;
}

.game .board .spot .card-render img {
  visibility: visible;
  width: 5em;
  height: 5em;
}

.game .deck-back-render {
  border: 1px solid gold;
  margin: 3px 3px;
  width: 10em;
  height: 18em;
  background: url('/game/resources/app/img/card-back.jpeg');
  background-size: 100% 100%;
}

.glow {
  box-shadow: 1px 1px 10px 3px lightblue;
  cursor: pointer;
}

.game .card-render {
  background: black;
  margin: 2px;
  overflow: scroll;
  display: block;
  width: 15em;
  height: 30em;
  padding: 1em;
  margin: 1em;
  border: 2px solid gold;
}

.game .card-render.movable {
  border: 2px dashed lightblue;
}

.game .opponent .card-render {
    display: block;
    /* background: url('/game/resources/app/img/card-back.jpeg'); */
    background-size: 100% 100%;
    width: 10em;
    height: 20em;
    padding: 1em;
    margin: 1em;
    border: 2px solid gold;
}

.game .card-render .c-image img {
  object-fit: cover;
  object-position: center;
  height: 13em;
  pointer-events: none;
}

.game .spot .card-render {
  height: auto;
}

.game .spot .c-contentx {
  display: none;
}

.game .c-content:target {
  display: block;
}

.layouts {
  display: flex;
}

.card-render .c-image {
  max-width: 100%;
}

.card-meta {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
}

.card-meta input {
  max-width: 40%;
  margin: 1em !important;
}

.collection, .collection-item {
  background: black !important;
  color: white !important;
  border: none !important;
}

/***** MODAL DIALOG ****/
#modal {
  /* Underlay covers entire screen. */
  position: fixed;
  top:0px;
  bottom: 0px;
  left:0px;
  right:0px;
  background-color:rgba(0,0,0,0.5);
  z-index:1000;
                                                                      
  /* Flexbox centers the .modal-content vertically and horizontally */
  display:flex;
  flex-direction:column;
  align-items:center;
  /* Animate when opening */
  animation-name: fadeIn;
  animation-duration:150ms;
  animation-timing-function: ease;
}
                                                                      
#modal > .modal-underlay {
  /* underlay takes up the entire viewport. This is only
  required if you want to click to dismiss the popup */
  position: absolute;
  z-index: -1;
  top:0px;
  bottom:0px;
  left: 0px;
  right: 0px;
}
                                                                      
#modal > .modal-content {
  /* Position visible dialog near the top of the window */
  margin-top:10vh;
                                                                      
  /* Sizing for visible dialog */
  width:80%;
  max-width:600px;
  max-height:50vh;
  overflow-y:scroll;
                                                                      
  /* Display properties for visible dialog*/
  border:solid 1px #999;
  border-radius:8px;
  box-shadow: 0px 0px 20px 0px rgba(0,0,0,0.3);
  background-color:black;
  padding:20px;
                                                                      
  /* Animate when opening */
  animation-name:zoomIn;
  animation-duration:150ms;
  animation-timing-function: ease;
}
                                                                      
#modal.closing {
  /* Animate when closing */
  animation-name: fadeOut;
  animation-duration:150ms;
  animation-timing-function: ease;
}
                                                                      
#modal.closing > .modal-content {
  /* Aniate when closing */
  animation-name: zoomOut;
  animation-duration:150ms;
  animation-timing-function: ease;
}
                                                                      
@keyframes fadeIn {
  0% {opacity: 0;}
  100% {opacity: 1;}
}
                                                                      
@keyframes fadeOut {
  0% {opacity: 1;}
  100% {opacity: 0;}
}
                                                                      
@keyframes zoomIn {
  0% {transform: scale(0.9);}
  100% {transform: scale(1);}
}
                                                                      
@keyframes zoomOut {
  0% {transform: scale(1);}
  100% {transform: scale(0.9);}
}
                                                                      
@media (prefers-color-scheme: dark) {
  body, input {
    color: #FFF !important;
    background: #000 !important;
  }
                                                                      
  pre {
    color: #ddd;
    background: #222;
  }
}
                                                                      
@media (prefers-color-scheme: light) {
  body, input {
    background: #FFF !important;
    color: #222 !important;
  }
                                                                      
  pre {
    background: #ddd;
    color: #222;
  }
}
                                                                      
#loading {
  display: none;
  position: fixed;
  top: 50px;
  right: 50px;
  border: 16px solid #f3f3f3;
  border-top: 16px solid #555;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 8s linear;
}

#loading.htmx-request, #loading.shown {
  display: block !important;
}
                                                                      
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
                                                                      
@media only screen and (max-width: 1000px) {
  .primary {
    display: none;
  }
                                                   
  .tertiary {
    display: none;
  }
                                                                      
  body:has(.game) .tertiary {
    display: initial;
    width: 100%;
  }
                                                                      
  body:has(.game) .secondary {
    display: none;
  }

  .blank {
    width: 100vw;
  }
}

"""
