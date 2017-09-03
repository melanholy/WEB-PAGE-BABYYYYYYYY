import React from "react";

export default class NotFoundPage extends React.Component {
    render() {
        return <div className="col-sm-offset-3 col-sm-6 not-found-body">
            <h1 className="not-found-header" a>Страница не найдена</h1>
            <br />
            То, что вы ищете, не здесь.
            <br />
            <a href="{{ url_for('index') }}">Сходите куда-нибудь еще</a>
        </div>;
    }
}