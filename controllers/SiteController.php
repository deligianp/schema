<?php

namespace app\controllers;

use Yii;
use yii\filters\AccessControl;
use yii\web\Controller;
use yii\web\Response;
use yii\filters\VerbFilter;
use app\models\LoginForm;
use app\models\ContactForm;
use app\models\User;
use app\models\Notification;


class SiteController extends Controller
{
    /**
     * {@inheritdoc}
     */
    public $freeAccess = true;
    public function behaviors()
    {
        return [
            'ghost-access'=> [
                'class' => 'webvimark\modules\UserManagement\components\GhostAccessControl',
            ],
            'access' => [
                'class' => AccessControl::className(),
                'only' => ['logout'],
                'rules' => [
                    [
                        'actions' => ['logout'],
                        'allow' => true,
                        'roles' => ['@'],
                    ],
                ],
            ],
            'verbs' => [
                'class' => VerbFilter::className(),
                'actions' => [
                    'logout' => ['post'],
                ],
            ],
        ];
    }

    /**
     * {@inheritdoc}
     */
    public function actions()
    {
        return [
            'error' => [
                'class' => 'yii\web\ErrorAction',
            ],
            'captcha' => [
                'class' => 'yii\captcha\CaptchaAction',
                'fixedVerifyCode' => YII_ENV_TEST ? 'testme' : null,
            ],
        ];
    }

    /**
     * Displays homepage.
     *
     * @return string
     */
    public function actionIndex()
    {
        return $this->render('index');
    }

    /**
     * Login action.
     *
     * @return Response|string
     */
    // public function actionLogin($eppn,$persistent_id)
    // {
    //     if (!Yii::$app->user->isGuest) {
    //         return $this->goHome();
    //     }

    //     if (!empty($eppn))
    //     {   
    //         $identity=User::findByUsername($eppn);
    //         $identityHash=User::findByPersistentId($persistent_id);

    //         if (empty($identity) && empty($identityHash))
    //         {
    //             User::createNewUser($eppn, $persistent_id);
    //             $identity=$identity=User::findByUsername($eppn);
    //         }

    //         if (!empty($identity) && empty($identityHash))
    //         {
    //             $user=$identity;
    //         }
    //         else if ((empty($identity)) && (!empty($identityHash))) 
    //         {
    //             $user=$identityHash;
    //         }
    //         else if ($identity==$identityHash)
    //         {
    //             $user=$identity;
    //         }

    //         Yii::$app->user->login($user,3600*24);

    //         return $this->goHome();
    //     }
        
    // }

    public function actionAuthConfirmed($token)
    {
    
            
        if (empty($token))
        {
            return $this->render('login_error');
        }
        else
        {
            $query=new \yii\db\Query;

            $sql=$query->select('*')->from('auth_user')->where(['token'=>$token])->createCommand()->getRawSql();

            $result=Yii::$app->db2->createCommand($sql)->queryOne();
            
            $username=$result['username'];
            $persistent_id=$result['persistent_id'];

            $identity=User::findByPersistentId($persistent_id);
            
            if (empty($identity))
            {
                User::createNewUser($username, $persistent_id);
                $identity=User::findByUsername($username);
            }
            else
            {
                if ($identity->username!=$username)
                {
                    $identity->username=$username;
                }
            }

            Yii::$app->user->login($identity,0);

            return $this->goHome();
        }
        

        // $model->password = '';
        // return $this->render('login', [
        //     'model' => $model,
        // ]);
    }

    /**
     * Logout action.
     *
     * @return Response
     */
    public function actionLogout()
    {
        Yii::$app->user->logout();

        return $this->goHome();
    }

    /**
     * Displays contact page.
     *
     * @return Response|string
     */
    public function actionContact()
    {
        $model = new ContactForm();
        if ($model->load(Yii::$app->request->post()) && $model->contact(Yii::$app->params['adminEmail'])) {
            Yii::$app->session->setFlash('contactFormSubmitted');

            return $this->refresh();
        }
        return $this->render('contact', [
            'model' => $model,
        ]);
    }

    /**
     * Displays about page.
     *
     * @return string
     */
    public function actionAbout()
    {
        return $this->render('about');

    }

    // public function actionPrivacy()
    // {
    //     return $this->render('privacy');
    // }

   
    public function actionNotificationRedirect($id)
    {
        $notification=Notification::find()->where(['id'=>$id])->one();

        $notification->markAsSeen();

        return $this->redirect($notification->url);


    }

    public function actionMarkAllNotificationsSeen()
    {
        Notification::markAllAsSeen();
    }

    public function actionNotificationHistory()
    {
        $typeClass=[Notification::DANGER=>'notification-danger', Notification::NORMAL=>'', 
                    Notification::WARNING=>'notification-warning', Notification::SUCCESS=>'notification-success'];
        $results=Notification::getNotificationHistory();
        $pages=$results[0];
        $notifications=$results[1];


        return $this->render('notification_history',['notifications'=>$notifications,'pages'=>$pages,'typeClass'=>$typeClass,]);
    }

    public function actionCwlTutorial()
    {
        return $this->render('cwl_tutorial');
    }


}
