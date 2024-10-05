## Project Leo

cardcraft, as a working title.
A demo running against devnet is up on https://cardcraft.ix.tc

> NOTE: PUBLIC CODE IN THIS PROJECT IS FULLY OPEN AND ACCESSIBLE, PARTS ARE GENERATED FROM A MORE EFFICIENT INTERNAL IMPLEMENTATION DESIGNED TO SAFEGUARD PROPRIETARY ELEMENTS.

## Contents

  - [Installation](#Installation)
  - [Updates](#Updates)
  - [Usage](#Usage)
  - [Development](#Development)
  - [Patterns](#Patterns)
    - [Polylith](#Polylith)
    - [Hiccup](#Hiccup)
    - [Miller columns](#Miller columns)
    - [Minimal CI/CD](#Minimal CI/CD)
    
## Installation

To install, run

```bash
wget https://raw.githubusercontent.com/licinaluka/cardcraft/refs/heads/master/config/deploy.sh | sh -
```
(TBD)

NOTE: This script WILL NOT install OS level dependencies, but will dry run to notify/warn about their presence and guide the user through installing them.

## Updates

To update your installation, run

```bash
wget https://raw.githubusercontent.com/licinaluka/cardcraft/refs/heads/master/config/update.sh | sh -
```
(TBD)

## Usage

Once installed, navigate to `./projects/cardcraft-web` and start 3rd party dependencies

```bash
docker-compose up -d
```

then run ./start.sh

## Development

As will be further detailed in Patterns/[Minimal CI/CD](#Minimal CI/CD) the approach taken for early developments is minimal enough to help with one-click deployment, that is, one command deployment.

Capistrano is used to deploy to live environments, and any of the deployment tasks will first try to pass all typechecks and all unit tests.

Similarly, just running

```bash
bundle exec cap prod typechecks
```
and

```bash
bundle exec cap prod tests
```
and

```bash
bundle exec cap prod pokes
```

will trigger the checkers to verify code changes. These can be added to a pre-commit hook but are not a requirement.

---

As will also be detailed in Patterns/[Polylith](#Polylith) the code is structured out into a bases, components, projects structure in order to support the complex monorepo needs of a system such as this. As can be seen in only-planned projects no matter what kind of deployable software unit is built, this structure will support it.

## Patterns

To detail some of the architectural and design patterns taken while building out the system.

### Polylith

Polylith is a monorepo approach that makes it easier to maintain complex systems. It assists in easily breaking up monoliths into microservices and the other way around.

This repository does not leverage additional tooling for its polylith and uses symlinks instead, but there is tooling such as 

https://davidvujic.github.io/python-polylith-docs/

More info https://polylith.gitbook.io/polylith

### Hiccup & hypermedia

HAML, Pugjs, Jade, Goht, Hiccup.
This project uses PyHiccup which is basically a template engine that turns

```python
["li", ["a", {"href": "/"}, "HOME"]]
```

into

```html
<li><a href="/">HOME</a></li>
```

it is a tremendous boost when creating web-based interactions.

In a similar manner, HTMX and concepts learned from https://hypermedia.systems help breaking up a dynamic web application into partials to build out an actual RESTful HATEOAS API.

This, then, means that for a RESTful JSON API all you need to do is respond with json instead of the hiccup template and you have yourself an API.

Keeping an MVC structure for code behind each part helps tremendously with quickly building out a full web application while having a small mental burden. You can always immediately find what you're looking for.

### Miller columns

Points about hiccup and hypermedia do stand on their own, but in order to build out a dynamic responsive web application - and a stable foundation for additional features further on -  in a short amount of time a stable UX concept is needed.

For this we leverage a limited version of what's known as Miller columns.

It's a very effective method of segregating digital functionalities in a visual way. You always know where something belongs.

More info:

https://en.wikipedia.org/wiki/Miller_columns

https://insidegovuk.blog.gov.uk/2014/07/15/improving-gov-uks-navigation/



### Minimal CI/CD

Capistrano. `bundle exec cap environment_here task_here` and you're set.

Write a Ruby block into config/deploy.rb and some environment config into config/deploy/environment_here.rb and you can automate basically anything, on a remote machine, locally, whichever you need.

Once there's a need for an entire pipeline ecosystem it'll likely be gitlab CI/CD, but for now capistrano works best. Fabric could work as well but we had more luck with setting up capistrano quickly.