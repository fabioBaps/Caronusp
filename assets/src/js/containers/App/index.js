import React from 'react';
import Title from '../../components/Title';
import { useState } from 'react';
import Header from '../../components/Header';
import Introduction from '../../components/Introduction';
import Articles from '../../components/Articles';
import article1 from '../../content/article1';
import article2 from '../../content/article2';
import article3 from '../../content/article3';

const articlesData = [article1, article2, article3];

class App extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      selectedArticle: null,
    };
  }

  toggleArticle = (articleId) => {
    this.setState((prevState) => ({
      selectedArticle: prevState.selectedArticle === articleId ? null : articleId,
    }));
  };

  render () {
    const { selectedArticle } = this.state;
    const text = 'Sobre';
    return (
      
      <div className="app">
        <Header />
        <Title text={text} />
        <main>
          <Introduction />
          <Articles
            articles={articlesData}
            selectedArticle={selectedArticle}
            onToggleArticle={this.toggleArticle}
          />
        </main>
      </div>
    )
  }
}
export default App;
