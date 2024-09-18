def theme():
    return """
.document {
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
.miller-column {
  flex-grow: 1;
  margin: 1em;
}
.miller-column.primary {
  width: 16%;
}
.miller-column.secondary {
  width: 32%;
  overflow: auto;
  height: 100vh;
}
.miller-column.tertiary {
  width: 50%;
  overflow:auto;
  height: 100vh;
                                                                      
  scroll-behavior: smooth;
}
.miller-column.secondary a[disabled=true] {
  pointer-events: none;
}
                                                                      
.document {
  padding: 2em;
  font-family: monospace;
}
.document *:hover {
  border-left: none;
}
.document *:target {
  /** background: #FBF719; */
  /** text-decoration: underline; */
  /** text-decoration-color: #673ab7; */
  padding-left: 0.2em;
  border-left: 2px solid #888;
}
.document > div {
  margin: 1em;
}
.document nav a {
  color: #111;
}
.document.web {
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
                                                                      
                                                                      
.document ul:not(.browser-default) {
  padding-left: revert;
}
.document ul:not(.browser-default)>li {
  list-style-type: initial;
}
                                                                      
.document ol:not(.browser-default) {
  padding-left: revert;
}
.document ol:not(.browser-default)>li {
  /* list-style-type: initial; */
}
                                                                      
#anchors a:target {
    font-weight: bold;
    color: red;
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
  animation: spin 2s linear infinite;
}
                                                                      
#loading.htmx-request {
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
                                                                      
  body:has(.document) .tertiary {
    display: initial;
    width: 100%;
  }
                                                                      
  body:has(.document) .secondary {
    display: none;
  }
"""
