import React from 'react';
import Header from './header.jsx';
import Aside from './aside.jsx';

export default class Base extends React.Component {
    render() {
        return <div>
            <Header />
            <Aside />
            <main className="container">
                <div className="content">
                    {this.props.body}
                </div>
            </main>
        </div>;
    }
}
