from distutils.core import setup
setup(
  name = 'sentimentr',       
  packages = ['sentimentr'],   
  version = '####ADD VERSION HERE####',
  package_data = {'sentimentr': ['lexica/*.txt']},  
  license='MIT',        
  description = 'Context-aware sentiment analysis model for formal and informal social media-style parlance',   
  author = 'Mohammad Darwich',                   
  author_email = 'modarwish@hotmail.com',     
  url = 'https://github.com/modarwish1/sentimentr',   
  download_url = '####ADD URL HERE####',    
  keywords = ['sentiment analysis', 'opinion mining', 'sentiment strength', 'sentiment lexicon', 'sentiment dictionary', 'informal text', 'internet slang', 'social media'],   
  install_requires=[           
          'nltk',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',    
    'Intended Audience :: Developers',     
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',    
  ],
)
