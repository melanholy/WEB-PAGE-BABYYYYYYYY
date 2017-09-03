import React from 'react';
import Contacts from './contacts.jsx';
import Bio from './bio.jsx';

export default class MainPage extends React.Component {
    render() {
        return <div>
            <h1 className="about-header">Всем здрасьте</h1>
            <section className="row">
                <Bio />
            </section>
            <hr />
            <section className="row">
                <Contacts />
            </section>
        </div>;
    }
}
