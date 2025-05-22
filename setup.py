from setuptools import setup, find_packages

setup(
    name="mealrecommender",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "seleniumbase",
        "bs4",
        "pandas",
        "pycli",
        "requests",
        "beautifulsoup4"
    ],
    author="Anton Persson",
    author_email="Antonnilspersson@gmail.com",
    description="A web scraper and meal recommender (machine learning) for Mercadona.",
    keywords="web scraper, mercadona, food prices, machine learning, meal recommender",
    url="https://github.com/antonnpersson/mealrecommender",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "mealrecommender=mealrecommender.app:main",
        ],
    },
)