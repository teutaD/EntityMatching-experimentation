# Sharing the Neo4j EDA Notebook

## Google Colab Integration

### ✅ Colab Badge Added

The notebook now includes a "Open in Colab" badge at the top. When you push this notebook to GitHub, users can click the badge to open it directly in Google Colab.

### How It Works

1. **Push to GitHub**: Commit and push the notebook to your GitHub repository
2. **Click the Badge**: Users click the Colab badge in the notebook
3. **Opens in Colab**: The notebook opens in Google Colab automatically
4. **Run in Cloud**: Users can run the notebook without local setup

### Colab URL Format

```
https://colab.research.google.com/github/{username}/{repo}/blob/{branch}/{path}
```

**Current Configuration:**
```
https://colab.research.google.com/github/teutedrini/OntoAligner/blob/main/eda/neo4j_eda_analysis.ipynb
```

### Updating the Badge

If you need to change the GitHub username, repository name, or branch, edit the badge URL in the first cell:

```html
<a href="https://colab.research.google.com/github/YOUR_USERNAME/YOUR_REPO/blob/main/eda/neo4j_eda_analysis.ipynb" target="_parent">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a>
```

## Other Sharing Options

### 1. **Direct Colab Link**

Share the direct Colab URL:
```
https://colab.research.google.com/github/teutedrini/OntoAligner/blob/main/eda/neo4j_eda_analysis.ipynb
```

### 2. **NBViewer**

For read-only viewing with better rendering:
```
https://nbviewer.org/github/teutedrini/OntoAligner/blob/main/eda/neo4j_eda_analysis.ipynb
```

### 3. **GitHub Direct View**

GitHub renders notebooks natively:
```
https://github.com/teutedrini/OntoAligner/blob/main/eda/neo4j_eda_analysis.ipynb
```

### 4. **Binder**

For interactive execution without Colab:
```
https://mybinder.org/v2/gh/teutedrini/OntoAligner/main?filepath=eda/neo4j_eda_analysis.ipynb
```

### 5. **JupyterLab/Jupyter Notebook**

For local execution:
```bash
cd eda
pipenv run jupyter notebook neo4j_eda_analysis.ipynb
```

## Adding Badges to README

You can add multiple badges to your README.md:

```markdown
# Neo4j EDA Analysis

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/teutedrini/OntoAligner/blob/main/eda/neo4j_eda_analysis.ipynb)
[![NBViewer](https://img.shields.io/badge/render-nbviewer-orange.svg)](https://nbviewer.org/github/teutedrini/OntoAligner/blob/main/eda/neo4j_eda_analysis.ipynb)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/teutedrini/OntoAligner/main?filepath=eda/neo4j_eda_analysis.ipynb)
```

## Using Colab with Private Repositories

### Option 1: Make Repository Public
The easiest way - Colab can directly access public GitHub repos.

### Option 2: Use GitHub Authentication
1. Open Colab
2. Go to File → Open notebook
3. Select "GitHub" tab
4. Authenticate with GitHub
5. Access private repositories

### Option 3: Upload Directly to Colab
1. Download the notebook
2. Go to Colab
3. File → Upload notebook
4. Select the .ipynb file

## Colab-Specific Considerations

### Installing Dependencies

Add a cell at the beginning for Colab users:

```python
# Install dependencies (uncomment if running in Colab)
# !pip install neo4j pandas matplotlib seaborn ydata-profiling
```

### Mounting Google Drive

For saving results in Colab:

```python
# Mount Google Drive (uncomment if running in Colab)
# from google.colab import drive
# drive.mount('/content/drive')
```

### Cloning the Repository

To access the `neo4j_analyzer` package in Colab:

```python
# Clone repository (uncomment if running in Colab)
# !git clone https://github.com/teutedrini/OntoAligner.git
# import sys
# sys.path.append('/content/OntoAligner/eda')
```

## Best Practices

### 1. **Add Setup Instructions**
Include a cell explaining how to set up the environment in Colab.

### 2. **Handle File Paths**
Use relative paths that work both locally and in Colab.

### 3. **Provide Sample Data**
Include sample data or instructions for accessing data.

### 4. **Document Requirements**
List all required packages and their versions.

### 5. **Test in Colab**
Always test the notebook in Colab before sharing.

## Troubleshooting

### Badge Not Working
- Ensure the notebook is pushed to GitHub
- Check the URL format is correct
- Verify the repository is public (or user is authenticated)

### Dependencies Not Found
- Add installation cells for Colab users
- Include requirements.txt in the repository

### Module Import Errors
- Ensure the package structure is correct
- Add the package directory to sys.path

### Connection Issues
- Neo4j must be publicly accessible or use SSH tunneling
- Update connection settings for remote access

## Example README Section

Add this to your main README.md:

```markdown
## 📓 Interactive Notebook

Explore the Neo4j Property Analyzer interactively:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/teutedrini/OntoAligner/blob/main/eda/neo4j_eda_analysis.ipynb)

The notebook includes:
- Database exploration
- Property analysis (Fast & Standard modes)
- Interactive visualizations
- Performance monitoring
- Results export

See [NOTEBOOK_GUIDE.md](eda/NOTEBOOK_GUIDE.md) for detailed instructions.
```

## Additional Resources

- [Google Colab Documentation](https://colab.research.google.com/notebooks/intro.ipynb)
- [Jupyter Notebook Best Practices](https://jupyter-notebook.readthedocs.io/)
- [NBViewer Documentation](https://nbviewer.org/)
- [Binder Documentation](https://mybinder.readthedocs.io/)

