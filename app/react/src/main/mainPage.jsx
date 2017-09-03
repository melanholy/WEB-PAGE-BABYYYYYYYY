import React from 'react';
import Contacts from './contacts.jsx';
import About from './about.jsx';

export default class MainPage extends React.Component {
    render() {
        return <div>
            <h1>Всем здрасьте</h1>
            <About />
            <hr />
            <Contacts />
        </div>;
    }
}
