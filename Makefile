
.SILENT:

LAB_PATH = lab

clear:
	clear

lab_mariadb_get:
	echo "\033[31mSetting up the MariaDB lab environment...\033[0m"
	git clone https://github.com/yuyudhn/SQLi-Labs-Docker.git $(LAB_PATH)/SQLi-Labs-Docker || true
	rm $(LAB_PATH)/SQLi-Labs-Docker/docker-compose.yml
	cp $(LAB_PATH)/docker-compose.yml $(LAB_PATH)/SQLi-Labs-Docker/
	cd $(LAB_PATH)/SQLi-Labs-Docker && docker-compose up --build -d 

lab_mysql_post:
	echo "\033[31mSetting up the MySQL lab environment...\033[0m"
	if [ ! -d "$(LAB_PATH)/startrek_payroll-Docker" ]; then \
		git clone https://github.com/thomaslaurenson/startrek_payroll.git $(LAB_PATH)/startrek_payroll-Docker; \
	fi
	cd $(LAB_PATH)/startrek_payroll-Docker && docker rm -f startrek-payroll-mysql || true
	cd $(LAB_PATH)/startrek_payroll-Docker && docker rm -f startrek-payroll-php || true
	cd $(LAB_PATH)/startrek_payroll-Docker && docker rm -f startrek-payroll-nginx || true
	cd $(LAB_PATH)/startrek_payroll-Docker && docker-compose up --build -d

ps_rule:
	docker ps

labs: clear lab_mariadb_get lab_mysql_post  ps_rule
	

clean_labs:
	# if [ -d "$(LAB_PATH)/SQLi-Labs-Docker" ]; then \
	# 	if [ -f "$(LAB_PATH)/SQLi-Labs-Docker/docker-compose.yml" ]; then \
	# 		cd $(LAB_PATH)/SQLi-Labs-Docker && docker-compose down; \
	# 	fi; \
	# 	cd ../../ && rm -rf $(LAB_PATH)/SQLi-Labs-Docker; \
	# fi
	# if [ -d "$(LAB_PATH)/startrek_payroll-Docker" ]; then \
	# 	rm -rf $(LAB_PATH)/startrek_payroll-Docker; \
	# fi
	if [ -d "$(LAB_PATH)" ]; then \
		find $(LAB_PATH) -mindepth 1 ! -name "docker-compose.yml" -exec rm -rf {} +; \
	fi
	docker ps -q | xargs -r docker stop
	docker ps -aq | xargs -r docker rm
	docker network prune -f
	docker ps
	
clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +


run: clear
	python3 ./core/vaccine.py http://localhost:1338/
	echo
	python3 ./core/vaccine.py -X POST -o mysql_post_login.txt http://localhost:8080/


fclean: clean clean_labs clear
	if [ -d "data" ]; then \
		rm -rf data/*; \
	fi
	echo "Finished cleaning bye bye"


re : fclean clean_labs labs run