import React from "react";

export default class About extends React.Component {
    render() {
        return <section className="row">
            <h2>Кто я такой?</h2>
            <figure className="col-sm-5 col-md-4 col-xs-12" style="padding: 0;">
                <div style="overflow: hidden;">
                    <img src="{{ url_for('static', filename='portrait.jpg') }}" alt="Автопортрет" className="img-responsive" />
                </div>
                <figcaption>Точный автопортрет</figcaption>
            </figure>
            <div className="col-sm-7 col-md-8 col-xs-12 about">
                <p>
                    Меня зовут Кошара Павел. Я учусь в
                    <a href="http://urfu.ru" target="_blank">УрФУ</a>
                    на факультете
                    <a href="http://imkn.urfu.ru/" target="_blank">ИМКН</a>
                    по специальности "Компьютерная безопасность".
                    <br />
                    Дотянул уже до
                    <span style="text-decoration: line-through;">первого</span>
                    <span style="text-decoration: line-through;">второго</span>
                    третьего курса.
                </p>
                <p>
                    Я живу хорошо, просто замечательно. У меня все есть, есть свой дом - он теплый.
                    <br />
                    В нем одна комната и кухня.
                </p>
                <p>
                    А здоровье мое не очень: то лапы ломит, то хвост отваливается.
                </p>
                <p>
                    А на днях я линять начал. Старая шерсть с меня сыплется, хоть в дом не заходи...
                    Зато новая растет - чистая-шелковистая.
                    <br />
                    Так что лохматость у меня повысилась.
                </p>
                <span className="pull-right">
                        До свидания, ваш друг - дядя Шарик.
                    </span>
            </div>
        </section>;
    }
}