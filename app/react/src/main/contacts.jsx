import React from "react";

export default class Contacts extends React.Component {
    render() {
        return <section>
            <h2>Как меня найти?</h2>
            <div className="col-sm-4 contact-wrapper">
                <a href="https://vk.com/4d5354353" target="_blank">
                    <span>Написать телеграмму</span>
                    <br />
                    <img className="img-responsive contact-img" src="{{ url_for('static', filename='telegraph.png') }}" alt="Телеграф" />
                </a>
            </div>
            <div className="col-sm-4 contact-wrapper">
                <a href="mailto:irrygan@gmail.com">
                    <span>Отправить голубя</span>
                    <br />
                    <img className="img-responsive contact-img" src="{{ url_for('static', filename='pigeon.png') }}" alt="Голубь" />
                </a>
            </div>
            <div className="col-sm-4 contact-wrapper">
                <a href="https://github.com/melanholy" target="_blank">
                    <span>Профиль GitHub</span>
                    <br />
                    <img className="img-responsive contact-img" src="{{ url_for('static', filename='sir_octocat.png') }}" alt="Октокот" />
                </a>
            </div>
        </section>;
    }
}