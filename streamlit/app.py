import streamlit as st
import requests
from datetime import datetime

import os

# BACKUP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backups"))
BACKUP_DIR = "/home/alexander/DB_CP/backups"

API_URL = "http://localhost:8000"

 

# --- Функция для авторизации ---
def login():

    st.title("Авторизация")
    email = st.text_input("Почта")
    password = st.text_input("Пароль", type="password")
    
    if st.button("Войти"):
        response = requests.post(f"{API_URL}/login", json={"mail": email, "password": password})
        if response.status_code == 200:
            token = response.cookies.get("users_access_token")
            st.session_state.token = token
            st.success("Успешная авторизация!")
            st.stop()
        else:
            st.error("Неверная почта или пароль.")

def register():
    st.title("Регистрация")
    name = st.text_input("Имя и Фамилия")
    phone_number = st.text_input("Номер телефона")
    mail = st.text_input("Почта")
    address = st.text_input("Адрес")
    birth = st.date_input("Дата рождения")
    sex = st.selectbox("Пол", ["male", "female"])
    tabel_number = st.text_input("Табельный номер")
    segment = st.text_input("Сегмент")
    function = st.text_input("Функция")
    password = st.text_input("Пароль", type="password")
    
    if st.button("Зарегистрироваться"):
        data = {
            "user_data": {
                "name": name,
                "phone_number": phone_number,
                "mail": mail,
                "address": address,
                "birth": str(birth),
                "sex": sex,
                "tabel_number": tabel_number,
                "segment": segment,
                "function": function
            },
            "password_data": {
                "password": password
            }
        }
        response = requests.post(f"{API_URL}/registration", json=data)
        
        if response.status_code == 200:
            st.success("Регистрация успешна!")
        else:
            st.error("Ошибка регистрации.")
            
            if isinstance(response.json()["detail"], str):
                st.error(response.json()["detail"])

            else:
                for i in range(len(response.json()["detail"])):
                    st.error(response.json()["detail"][i]["msg"] + "\n\nПоле: " + response.json()["detail"][i]["loc"][2])

# --- Функция для личного кабинета ---
def personal_cabinet():
    st.title("Личный кабинет")
    
    if "token" not in st.session_state:
        st.error("Вы не авторизованы!")
        return
    
    logout_button = st.button(f"Выйти из профиля")
    
    
    
    if logout_button:
        response = requests.post(f"{API_URL}/logout/")
        if response.status_code == 200:
            if "token" in st.session_state:
                del st.session_state.token
            st.success("Вы вышли из профиля")
            return
        else:
            st.error("Ошибка")
            
            
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    user_response = requests.get(f"{API_URL}/me/", headers=headers)
    if user_response.status_code == 200:
        user_data = user_response.json()
        st.write("Добро пожаловать,", user_data["name"])
        st.subheader("Информация о пользователе")
        
        st.text(f"Номер телефона: {user_data['phone_number']}")
        st.text(f"Электронная почта: {user_data['mail']}")
        st.text(f"Адрес: {user_data['address']}")
        st.text(f"Дата рождения: {str(user_data['birth'])}")
        st.text(f"Пол: {'Мужской' if user_data['sex'] == 'male' else 'Женский'}")
        st.text(f"Табельный номер: {user_data['tabel_number']}")
        st.text(f"Сегмент: {user_data['segment']}")
        st.text(f"Должность: {user_data['function']}")
        
        st.markdown("---") 
        
        if "show_pers_promos" not in st.session_state:
            st.session_state.show_pers_promos = False 
        
        show_promos_button = st.button(f"Показать мои промокоды")
        
        if show_promos_button:
            st.session_state.show_pers_promos = not st.session_state.show_pers_promos
        

        if st.session_state.show_pers_promos:
            promo_response = requests.get(f"{API_URL}/users/{user_data['user_id']}/promos")
            if promo_response.status_code == 200:
                promos = promo_response.json()
                if promos:
                    for promo in promos:
                        with st.expander(f"Промокод: {promo['promo']}"):
                            st.write(f"**Действителен с:** {promo['valid_from']}")
                            st.write(f"**Действителен до:** {promo['valid_to']}")
                            st.write(f"**Тип:** {promo['type']}")
                            st.write(f"**Активирован:** {'Да' if promo['activated_on'] else 'Нет'}")

                            if not promo['activated_on']:
                                st.error(f"Промокод {promo['promo']} еще не активирован! Активируйте его, пока он действителен.")
                                activate_button = st.button(f"Активировать промокод {promo['promo']}", key=f"activate_{promo['promo_id']}")
                                if activate_button:
                                    activate_response = requests.put(f"{API_URL}/promos/{promo['promo_id']}/activate", headers=headers)
                                    if activate_response.status_code == 200:
                                        st.success(f"Промокод {promo['promo']} успешно активирован!")
                                    else:
                                        st.error("Не удалось активировать промокод.")
                            else:
                                st.success(f"Промокод {promo['promo']} уже активирован!")
                else:
                    st.write("У вас нет активных промокодов.")
            else:
                st.error("У вас нет активных промокодов.")
        
        st.markdown("---") 
        
        if "is_editing" not in st.session_state:
            st.session_state.is_editing = False 
        
        edit_button = st.button(f"Редактировать информацию о пользователе")
        
        if edit_button:
            st.session_state.is_editing = not st.session_state.is_editing
        
        if st.session_state.is_editing:
            st.subheader("Редактирование информации")
            
            with st.form("edit_form"):
                name = st.text_input("Имя", user_data["name"])
                phone_number = st.text_input("Номер телефона", user_data["phone_number"], disabled= True)
                mail = st.text_input("Электронная почта", user_data["mail"], disabled=True) 
                address = st.text_input("Адрес", user_data["address"])
                birth = st.date_input("Дата рождения", datetime.strptime(user_data['birth'], "%Y-%m-%d").date())
                sex = st.selectbox("Пол", options=["male", "female"], index=0 if user_data["sex"] == "male" else 1, disabled= True)
                tabel_number = st.number_input("Табельный номер", value=user_data["tabel_number"])
                segment = st.text_input("Сегмент", user_data["segment"])
                function = st.text_input("Функция", user_data["function"])
                
                submitted = st.form_submit_button("Сохранить изменения")
                
                if submitted:
                    updated_data = {
                        "name": name,
                        "phone_number": phone_number,
                        "mail": mail,  
                        "address": address,
                        "birth": birth.isoformat(),
                        "sex": sex,
                        "tabel_number": tabel_number,
                        "segment": segment,
                        "function": function
                    }
                    
                    update_response = requests.put(f"{API_URL}/edit_me/", headers=headers, json=updated_data)
                    
                    if update_response.status_code == 200:
                        st.success("Данные успешно обновлены!")
                    else:
                        st.error(f"Ошибка обновления данных")
                        if isinstance(update_response.json()["detail"], str):
                            st.error(update_response.json()["detail"])

                        else:
                            for i in range(len(update_response.json()["detail"])):
                                st.error(update_response.json()["detail"][i]["msg"] + "\n\nПоле: " + 
                                         update_response.json()["detail"][i]["loc"][1])
        st.markdown("---")                            
        
    else:
        st.error("Не удалось получить данные пользователя.")
        st.json(user_response.json())

    # Просмотр питомцев
    st.subheader("Мои питомцы")
    # if st.button("Показать моих питомцев"):
    pets_response = requests.get(f"{API_URL}/my_pets", headers=headers)
    if pets_response.status_code == 200:
        pets = pets_response.json()
        
        if pets:
            for pet in pets:
                st.subheader(f"Имя: {pet['name']}")
                # st.text(f"pet_id: {pet['pet_id']}")
                st.text(f"Пол: {'Мужской' if pet['sex'] == 'male' else 'Женский'}")
                st.text(f"Животное: {pet['animal']}")
                st.text(f"Порода: {pet['breed']}")
                st.text(f"Дата рождения: {pet['birth']}")
                st.text(f"Вес: {pet['weight']} кг")
                st.text(f"Стерилизован: {'Да' if pet['sterilized'] else 'Нет'}")
                
                if pet['diseases']:
                    st.text("Болезни:")
                    for disease in pet['diseases']:
                        st.text(f"- {disease['disease_name']} (Опасность: {disease['disease_danger']})")
                else:
                    st.text("Болезни: Нет информации")

                if pet['feeds']:
                    st.text("Корм:")
                    for feed in pet['feeds']:
                        st.text(f"- {feed['feed_name']} (Тип: {feed['feed_type']})")
                else:
                    st.text("Корм: Нет информации")
                
                if "pet_editing" not in st.session_state:
                    st.session_state.pet_editing = False 
            
                pet_edit_button = st.button(f"Редактировать информацию о животном: {pet['name']}", key=f"edit_button_{pet['pet_id']}")
                
                if pet_edit_button:
                    st.session_state.pet_editing = not st.session_state.pet_editing
                    
                if st.session_state.pet_editing:
                    st.subheader("Редактирование информации")
    
                    with st.form(f"edit_form: {pet['name']}"):
                        name = st.text_input("Имя", pet["name"])
                        sex = st.selectbox("Пол", options=["male", "female"], format_func=lambda x: "Мужской" if x == "male" else "Женский", disabled= True)
                        animal_type = st.text_input("Животное", pet["animal"]) 
                        breed = st.text_input("Порода", pet["breed"])
                        birth = st.date_input("Дата рождения", datetime.strptime(pet['birth'], "%Y-%m-%d").date())
                        weight = st.number_input("Вес (в кг)", min_value=0, value=pet['weight'])
                        sterilized = st.checkbox("Стерилизован", value = pet['sterilized'])
                        
                        
                        st.subheader("Болезни питомца")
        
                        updated_diseases  = []

                        # Обработка существующих болезней
                        if pet['diseases']:
                            for idx, disease in enumerate(pet['diseases']):
                                disease_name = st.text_input(f"Болезнь {idx + 1}", disease["disease_name"], key=f"disease_name_{idx}")
                                disease_danger = st.number_input(f"Опасность {idx + 1}", min_value=0, max_value=10, value=disease["disease_danger"], key=f"disease_danger_{idx}")

                                if disease_name.strip():  # Проверка на пустую строку
                                    updated_diseases.append({
                                        "disease_name": disease_name,
                                        "disease_danger": disease_danger
                                    })
                        else:
                            st.info("У питомца нет болезней, но вы можете добавить информацию.")
                        
                    
                        # Добавление новой болезни
                        st.subheader("Добавить новую болезнь")
                        new_disease_name = st.text_input("Название болезни", key=f"new_disease_name_{pet['pet_id']}")
                        new_disease_danger = st.number_input("Опасность", min_value=0, max_value=10, key=f"new_disease_danger_{pet['pet_id']}")

                        if new_disease_name.strip():
                            updated_diseases.append({
                                "disease_name": new_disease_name,
                                "disease_danger": new_disease_danger
                        })
                        
                        # Информация о корме
                        st.subheader("Редактирование корма")
                        if pet["feeds"]:
                            feed_name = st.text_input("Название корма", pet["feeds"][0]["feed_name"])
                            feed_type = st.selectbox("Тип корма", options=["Сухой", "Влажный"], index=0 if pet["feeds"][0]["feed_type"] == "Сухой" else 1)
                        else:
                            st.info("У питомца нет информации о кормах, вы можете её добавить.")
                            feed_name = st.text_input("Название корма")
                            feed_type = st.selectbox("Тип корма", options=["Сухой", "Влажный"], key=f"feed_type_{pet['pet_id']}")
                            
                        submitted_pet_change = st.form_submit_button("Сохранить изменения")
                        
                        if submitted_pet_change:
                            pet_data = {
                                "pet_data": {
                                    "name": name,
                                    "sex": sex,
                                    "animal": animal_type,
                                    "breed": breed,
                                    "birth": str(birth),
                                    "weight": weight,
                                    "sterilized": sterilized
                                },
                                "disease_data": updated_diseases,
                                "feed_data": {
                                    "feed_name": feed_name,
                                    "feed_type": feed_type
                                } if feed_name else None
                            }
                         
                            # st.subheader("Данные питомца:")
                            # st.json(pet_data)
                            delete_response = requests.delete(f"{API_URL}/my_pets/{pet['pet_id']}", headers=headers)
                            if delete_response.status_code == 200:
                                # st.success(f"Питомец {pet['name']} успешно удален.")
                                pass
                            else:
                                st.error(f"Не удалось удалить питомца {pet['name']}.") 
                            
                            pet_response = requests.post(f"{API_URL}/my_pets/add_pets", json=pet_data, headers=headers)
                            if pet_response.status_code == 200:
                                # st.success("Питомец успешно добавлен!")
                                st.success("Данные о питомце успешно обновлены!")
                                pass
                            else:
                                st.error("Ошибка при добавлении питомца.")
                                st.json(pet_response.json())
                            
                        
                    
                delete_button = st.button(f"Удалить питомца: {pet['name']}", key=f"delete_{pet['name']}")
            
                if delete_button:
                    delete_response = requests.delete(f"{API_URL}/my_pets/{pet['pet_id']}", headers=headers)
                    if delete_response.status_code == 200:
                        st.success(f"Питомец {pet['name']} успешно удален.")
                        # st.stop()
                    else:
                        st.error(f"Не удалось удалить питомца {pet['name']}.")    
                    

                st.markdown("---")
        else:
            st.info("У вас пока нет зарегистрированных питомцев.")
    else:
        st.error("Не удалось загрузить список питомцев.")
        st.error(pets_response.json()["detail"])
           
    
    # Добавление питомца
    if "adding_pet" not in st.session_state:
            st.session_state.adding_pet = False 
        
    adding_pet_button = st.button(f"ДОБАВИТЬ НОВОГО ПИТОМЦА")
    
    if adding_pet_button:
        st.session_state.adding_pet = not st.session_state.adding_pet
    
    if st.session_state.adding_pet:    
        st.subheader("Добавить питомца")
        with st.form("pet_form"):
            st.subheader("Информация о питомце")
            pet_name = st.text_input("Имя питомца", max_chars=100)
            pet_sex = st.selectbox("Пол", options=["male", "female"], format_func=lambda x: "Мужской" if x == "male" else "Женский")
            animal_type = st.text_input("Тип животного", max_chars=50)
            breed = st.text_input("Порода", max_chars=50)
            birth_date = st.date_input("Дата рождения")
            weight = st.number_input("Вес (в кг)", min_value=0)
            sterilized = st.checkbox("Стерилизован", value=False)

            st.subheader("Информация о болезнях (опционально)")
            disease_name = st.text_input("Название болезни", max_chars=50, key="disease_name")
            disease_danger = st.number_input("Уровень опасности болезни", min_value=0, max_value=10, key="disease_danger")

            st.subheader("Информация о корме (опционально)")
            feed_name = st.text_input("Название корма", max_chars=50, key="feed_name")
            feed_type = st.selectbox("Тип корма", options=["Сухой", "Влажный"], key="feed_type")

            submitted = st.form_submit_button("Добавить питомца")

        if submitted:
            pet_data = {
                "pet_data": {
                    "name": pet_name,
                    "sex": pet_sex,
                    "animal": animal_type,
                    "breed": breed,
                    "birth": str(birth_date),
                    "weight": weight,
                    "sterilized": sterilized
                },
                "disease_data": [
                    {
                        "disease_name": disease_name,
                        "disease_danger": disease_danger
                    }
                ] if disease_name else [],
                "feed_data": {
                    "feed_name": feed_name,
                    "feed_type": feed_type
                } if feed_name else None
            }
            pet_response = requests.post(f"{API_URL}/my_pets/add_pets", json=pet_data, headers=headers)
            if pet_response.status_code == 200:
                st.success("Питомец успешно добавлен!")
            else:
                st.error("Ошибка при добавлении питомца.")
                st.json(pet_response.json())


def admin_panel():
    if "token" not in st.session_state:
        st.error("Вы не авторизованы!")
        return
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    
    response = requests.get(f"{API_URL}/check_admin/", headers=headers)
    user_data = response.json()
    if user_data['status_type'] == "admin":
    
        user_response = requests.get(f"{API_URL}/me/", headers=headers)
        if user_response.status_code == 200:
            user_data = user_response.json()
            st.write("Добро пожаловать,", user_data["name"], ", вам предоставлены права администратора")
            st.subheader("Информация о пользователе")
            
            st.text(f"Номер телефона: {user_data['phone_number']}")
            st.text(f"Электронная почта: {user_data['mail']}")
            st.text(f"Адрес: {user_data['address']}")
            st.text(f"Дата рождения: {str(user_data['birth'])}")
            st.text(f"Пол: {'Мужской' if user_data['sex'] == 'male' else 'Женский'}")
            st.text(f"Табельный номер: {user_data['tabel_number']}")
            st.text(f"Сегмент: {user_data['segment']}")
            st.text(f"Должность: {user_data['function']}")
        
        logout_button = st.button(f"Выйти из профиля")
        
        st.markdown("---")
        
        if logout_button:
            st.title("Страница администратора")
            response = requests.post(f"{API_URL}/logout/")
            if response.status_code == 200:
                if "token" in st.session_state:
                    del st.session_state.token
                st.success("Вы вышли из профиля")
                return
            else:
                st.error("Ошибка")
                
                
        if "show_users" not in st.session_state:
            st.session_state.show_users = False
        
        if st.button("Показать пользователей", key="load_users"):
            st.session_state.show_users = not st.session_state.show_users
        
        if st.session_state.show_users:
            st.header("Список пользователей")
                
            response = requests.get(f"{API_URL}/users")
            if response.status_code == 200:
                users =  response.json()
            else:
                st.error("Не удалось получить список пользователей.")
                users = []        
            
            if users:
                for user in users:
                    with st.expander(f"Пользователь: {user['name']}"):
                        st.write(f"**Имя:** {user['name']}")
                        st.write(f"**Email:** {user['mail']}")
                        st.write(f"**Номер телефона:** {user['phone_number']}")
                        st.write(f"**Адрес:** {user['address']}")
                        st.write(f"**Дата рождения:** {user['birth']}")
                        st.write(f"**Пол:** {'Мужской' if user['sex'] == 'male' else 'Женский'}")
                        st.write(f"**Табельный номер:** {user['tabel_number']}")
                        st.write(f"**Сегмент:** {user['segment']}")
                        st.write(f"**Функция:** {user['function']}")
                        st.write(f"**Последнее изменение профиля:** {user['last_updated']}")
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            button_key = f"show_promos_{user['user_id']}"
                            if button_key not in st.session_state:
                                st.session_state[button_key] = False  

                            if st.button(f"Показать промокоды {user['name']}", key=f"show_promos_button_{user['user_id']}"):
                                st.session_state[button_key] = not st.session_state[button_key]
                            
                            if st.session_state[button_key]:
                                promo_response = requests.get(f"{API_URL}/users/{user['user_id']}/promos")
                                
                                if promo_response.status_code == 200:
                                    promo_data = promo_response.json()
                                    
                                    if promo_data:
                                        st.write(f"**Промокоды пользователя {user['name']}:**")
                                        for promo in promo_data:
                                            st.write(f"**Промокод:** {promo['promo']}")
                                            st.write(f"**Срок действия:** с {promo['valid_from']} по {promo['valid_to']}")
                                            st.write(f"**Тип:** {promo['type']}")
                                            if promo['activated_on']:
                                                st.write(f"**Активирован:** {promo['activated_on']}")
                                            else:
                                                st.write("**Не активирован**")
                                            st.write("---")
                                    else:
                                        st.write("У этого пользователя нет промокодов.")
                                else:
                                    st.error("У этого пользователя нет промокодов.")
                        with col2:
                            if st.button("Выдать промокод", key=f"promo_{user['user_id']}"):
                                promo_response = requests.post(f"{API_URL}/users/{user['user_id']}/generate_promo")
                    
                                if promo_response.status_code == 200:
                                    promo_data = promo_response.json()
                                    st.success(f"Промокод успешно выдан: **{promo_data['promo']}**")
                                    st.write(f"**Действителен с:** {promo_data['valid_from']}")
                                    st.write(f"**Действителен до:** {promo_data['valid_to']}")
                                    st.write(f"**Тип:** {promo_data['type']}")
                                else:
                                    st.error("Не удалось выдать промокод.")
                
                
        st.markdown("---")   
        st.title("Управление резервными копиями базы данных")    
        backup_button = st.button("Создать резервную копию базы данных")
        if backup_button:
            try:
                response = requests.post(f"{API_URL}/backup/")
                if response.status_code == 200:
                    data = response.json()
                    st.success(f"Резервная копия успешно создана! 📂")
                    st.write(f"Файл: `{data['file']}`")
                else:
                    st.error(f"Ошибка при создании резервной копии: {response.text}")
            except Exception as e:
                st.error(f"Не удалось подключиться к серверу: {e}")
        
        downgrade_button = st.button("Откатить базу данных")
        
        if "downdrage_button" not in st.session_state:
            st.session_state.downdrage_button = False
        
        if downgrade_button:
            st.session_state.downdrage_button = not st.session_state.downdrage_button
        
        if st.session_state.downdrage_button:
            backup_files = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.dump')]
            if backup_files:
                for backup_file in backup_files:
                    with st.form(key=backup_file):
                        st.write(f"Бэкап: {BACKUP_DIR}/{backup_file}")
                        restore_button = st.form_submit_button(label=f"Откатиться к данной версии")
                        
                        if restore_button:
                            try:
                                response = requests.post(f"{API_URL}/restore/", json={"backup_file": backup_file})
                                if response.status_code == 200:
                                    st.success(f"База данных успешно откатилась к версии: {backup_file}")
                                else:
                                    st.error(f"Ошибка при восстановлении базы данных: {response.text}")
                            except Exception as e:
                                st.error(f"Не удалось подключиться к серверу: {e}")
                            
                                            
            else:
                st.warning("Нет доступных бэкапов для восстановления.")
        
        
    else:
        st.error("У вас недостаточно прав для функций администратора")


# --- Главный роутинг ---
page = st.sidebar.selectbox("Навигация", ["Авторизация", "Регистрация", "Личный кабинет", "Страница администратора"])

if page == "Авторизация":
    login()
elif page == "Регистрация":
    register()
elif page == "Личный кабинет":
    personal_cabinet()
elif page == 'Страница администратора':
    admin_panel()