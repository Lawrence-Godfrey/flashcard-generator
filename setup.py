from setuptools import setup, find_packages

setup(
    name="flashcard_generator",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "openai",
        "python-dotenv",
        "cryptography"
    ],
    entry_points={
        'console_scripts': [
            'generate_flashcards=generate_flashcards.generate_flashcards:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
