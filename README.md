# LogIt
For the Human Experience

Rate, review, and list anything. A Letterboxd-style app for everything you experience.

(The name is a nod to the ML term "logit", and it also just means "log it".)


## Overview

LogIt lets users keep lists of things they've experienced (movies, books, restaurants,
games, places, and more), rate and review each item, and share lists publicly or keep
them private.

Lists are organized into fixed categories and user-created topics. When a user searches
for a topic that doesn't exist, LogIt suggests similar topics other people have already
created, so the topic space stays clean instead of splitting into duplicates
("Coffee Shops" / "Cafes" / "coffee places"). If nothing fits, the user creates a new topic.


## Core Concepts

- User      An account.
- Category  Fixed, top-level grouping (e.g., Movies, Books, Food, Places, Games).
- Topic     User-created, belongs to a category. Stores a usage count and an embedding.
- List      A user's collection under one topic. Public or private.
- Item      The thing being rated (a specific movie, restaurant, book, etc.).
- Entry     A user's rating, review, and date for an item.

Key design decision: are Items shared across users (two people logging the same
restaurant point to one Item) or stored separately per list? Shared items make social
features and recommendations much easier later, but require handling duplicate items.


## Topic Suggestions

1. When a topic is created, embed its name with a sentence-embedding model and store
   the vector.
2. When a user searches, embed the query and run a nearest-neighbor search over
   existing public topics.
3. Keep only matches above a similarity threshold.
4. Rank matches by usage, or by a blended score:
       score = similarity + w * log(1 + usage)
5. If nothing passes the threshold, offer "Create new topic".

Privacy rule: topics that exist only on private lists are never suggested to other users.

Evaluation:
- Build a test set of 50-100 (search query -> expected topic) pairs covering synonyms,
  typos, plurals, near-misses, and queries that SHOULD create a new topic.
- Measure top-1 / top-3 accuracy and the false-suggestion rate on the "new topic" cases.
- Use it to tune the threshold and the weight w, and to compare embedding models.


## Roadmap

### Phase 0: Foundations
- [ ] Finalize data model (decide shared vs per-list Items)
- [ ] Choose stack; set up repo, CI, and deployment
- [ ] Seed the fixed categories

### Phase 1: Single-User Core Loop (MVP)
- [ ] Sign up / log in
- [ ] Create a list under a category and topic
- [ ] Add items; rate, review, and date entries
- [ ] View, edit, and delete your own lists
- [ ] Basic topic search with plain text / trigram matching
- [ ] Deploy and start using it daily
Done when: you can log real things for a week without friction.

### Phase 2: Embedding-Based Topic Suggestions
- [ ] Embed topics on creation; store vectors
- [ ] Nearest-neighbor search + threshold + usage ranking
- [ ] "Create new topic" fallback
- [ ] Log every topic search and its outcome (reused vs created)
- [ ] Build the eval set; tune threshold; compare 2-3 embedding models
Done when: top-3 accuracy on the eval set meets a target you set (e.g., 90%).

### Phase 3: Visibility and Social
- [ ] Public / private lists, with private topics excluded from suggestions
- [ ] Public profiles
- [ ] Browse public lists by topic
- [ ] Follow users; activity feed
- [ ] Invite 5-10 friends as testers
Done when: testers keep logging without being prompted.

### Phase 4: Expansion
- [ ] Merge near-duplicate topics; promote popular topics into official categories
- [ ] External APIs for fixed categories to autofill items (movies, books, places)
- [ ] Cross-category recommendations
- [ ] Mobile app


## Development Principles

- Build thin vertical slices: get each feature working end to end in rough form,
  ship it, then refine.
- Use the app yourself from day one.
- One feature at a time. Social features wait until logging and rating feel good.
- Protect the data model: prefer migrations over rewrites.
- Let logged search data drive tuning of topic suggestions.


## Metrics

- Topic reuse rate: share of topic searches that end in an existing topic
  (higher = less fragmentation; the main measure of whether suggestions work)
- Suggestion accuracy (offline): top-1 / top-3 on the eval set
- Weekly active loggers among testers
- Entries per user per week


## Tech Stack (TBD)

Suggested starting point:
- Web frontend first (faster to iterate than mobile)
- Postgres with pgvector for relational data and embeddings in one database
- A small open sentence-embedding model (e.g., all-MiniLM-L6-v2) or an embeddings API


## Open Questions

- Shared Items or per-list Items?
- Does a topic's usage count lists, unique users, or entries?
- Do private lists count toward a topic's usage?
- Should suggestions search within the chosen category only, or across all categories?
- Can a topic belong to more than one category?
