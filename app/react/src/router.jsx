import React from "react";
import {Location, Locations} from 'react-router-component';
import MainPage from './main/mainPage.jsx';
import NotFoundPage from './notFoundPage.jsx';

export default class Router extends React.Component {
    render() {
        return <Locations>
            <Location path='/' handler={MainPage} />
            <Location path='/404' handler={NotFoundPage} />
        </Locations>;
    }
}
