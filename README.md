# April
## ~9
- solve the problem that pre-processing is not well conducted

## 10-14
- enable to train and test
- using dog dataset
  - 2000 images
  - avg: 100 images per an image
- using resnet18
- 224×224
- acc: 46%。
- experiment similarly on  datasets below 
  -  car
  -  tower
  -  uspresident
## 21
- reserch dataset of existing research
- [Flickr30k Entities: Collecting Region-to-Phrase Correspondences for Richer Image-to-Sentence Models](https://arxiv.org/pdf/1505.04870.pdf)
  - text to image annotation
  - extend Flickr30k
  - mainly human, scene and clothes
  - problems: few images, similar meaning word(infant, baby)
  - annotation takes a lot of effort
    - using clowd sourcing method to collect annotation data
## 22-23
- reserch dataset of existing research
- [VTKEL: A resource for Visual-Textual-Knowledge Entity Linking](https://dl.acm.org/doi/pdf/10.1145/3341105.3373958?casa_token=dKJoNPVmxagAAAAA:5fR30eES4eC7qQ5_pYoppkbZiL3baE9JXVC0iz5umy08hlGj8v6IpwiePTXIZ20-l8bw6g4ozSaT)
  - visual-textual-knowledge entity linking
  - using entity extraction tool (PIKES)
  - link entity to YAGO Knowledge
- github: https://github.com/shahidost/VTKEL

## 24
- reserch dataset of existing research
- [Jointly Linking Visual and Textual Entity Mentions with Background Knowledge](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7298199/pdf/978-3-030-51310-8_Chapter_24.pdf)
  - some usable dataset is introduced in related work
  - entity link to flicker text
  - propose comprehensive method to create VTKEL dataset
- these papers are based on flicker, and assuming there is a dataset consisting of image and text
- it deviates from the propose of finding dataset for instance level recognition

## 29
- search paper from [Instance-level Recognition](https://towardsdatascience.com/instance-level-recognition-6afa229e2151)
- [Google Landmarks Dataset v2 A Large-Scale Benchmark for Instance-Level Recognition and Retrieval](https://arxiv.org/pdf/2004.01804.pdf)
  - used for kaggle in 2020
  - 5M images and 200k distinct instance labels
  - get images from wikimedia commons
  - there are no top-level category in wikimedia, so get category from google KG
  - anotated these images human work
  - re-annotation by showing and annotate some of highest confidenciak images
  - there many other landmark datasets for instance level recognition
  - no bounding box
- Conceptual Captions, coco

# May
### method to collect data 
- [icrawler](https://icrawler.readthedocs.io/en/latest/)
  - web crawler
  - search by keyword
  - quality of images are middle
- [機械学習のデータの集め方](https://qiita.com/nonbiri15/items/f5c5c4357458bfeb03bb)

# July
- each mL model learn in each domain to build model for each domain
- datasets have specific labels on each domain
- models predict only certtain domain
- [Google Knowledge Graph Search API](https://developers.google.com/knowledge-graph)
- build environment using docker iamge
