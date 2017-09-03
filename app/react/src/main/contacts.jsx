import React from 'react';

class ContactLink extends React.Component {
    render() {
        return <div className="col-sm-4 contact-wrapper">
            <a href="https://vk.com/4d5354353" target="_blank">
                <span>{this.props.caption}</span>
                <br />
                <img className="img-responsive contact-img" src={this.props.src} alt={this.props.alt} />
            </a>
        </div>;
    }
}

export default class Contacts extends React.Component {
    render() {
        return <div>
            <h2 className="about-row-header">Как меня найти?</h2>
            <ContactLink caption="Написать телеграмму" src="/static/telegraph.png" alt="Телеграф" />
            <ContactLink caption="Отправить голубя" src="/static/pigeon.png" alt="Почтовый голубь" />
            <ContactLink caption="Профиль GitHub" src="/static/sir_octocat.png" alt="Октокот" />
        </div>;
    }
}