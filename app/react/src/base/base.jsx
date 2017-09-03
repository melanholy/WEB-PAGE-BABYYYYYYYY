import React from 'react';
import Header from './header.jsx';
import Aside from './aside.jsx';

export default class Base extends React.Component {
    render(props) {
        return <div>
            <Header />
            <Aside />
            {props.body}
        </div>;
    }
}
