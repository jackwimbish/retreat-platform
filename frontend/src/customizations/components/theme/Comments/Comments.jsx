/**
 * Comments component.
 * @module components/theme/Comments/Comments
 */

import React, { useState, useEffect, useMemo } from 'react';
import PropTypes from 'prop-types';
import { useDispatch, useSelector } from 'react-redux';
import {
  addComment,
  deleteComment,
  updateComment,
  listMoreComments,
} from '@plone/volto/actions';
import { injectLazyLibs } from '@plone/volto/helpers/Loadable';
import { compose } from 'redux';
import { CommentEditModal } from '@plone/volto/components';
import { FormattedMessage, defineMessages, useIntl } from 'react-intl';
import { Container, Form as UiForm, Portal, Button } from 'semantic-ui-react';
import { Comment } from 'semantic-ui-react';
import Avatar from '@plone/volto/components/theme/Avatar/Avatar';
import Form from '@plone/volto/components/manage/Form/Form';
import Icon from '@plone/volto/components/theme/Icon/Icon';
import { flattenToAppURL } from '@plone/volto/helpers';

/**
 * Helper function to get the correct portrait URL
 * Handles the ++api++ prefix needed for Volto's development proxy
 */
const getPortraitUrl = (portrait) => {
  if (!portrait) return null;
  
  // In development, API URLs need the ++api++ prefix
  if (portrait.includes('/@portrait') && !portrait.includes('/++api++/')) {
    return portrait.replace('/@portrait', '/++api++/@portrait');
  }
  
  return flattenToAppURL(portrait);
};

/**
 * To get colors for avatars
 * An array of colors is defined (you can add or remove colors from it).
 * The index that'll be assigned as a color is a modulo of the addition
 * of ASCII decimal numbers composing the string, this will help to
 * get a unique color per user. The color is not saved so it'll be calculated
 * in every page refresh or accessing other pages with comments in it.
 *
 * The only issue here is when adding or removing colors from the list but
 * since it's not very likely to happen we can live with it for now.
 * @method getAvatarInternalColor
 * @param {String} fullName Name of the user (f.e. 'John Doe').
 * @returns {string} CSS color value from the list.
 */
const getAvatarInternalColor = (fullName) => {
  const colors = [
    '#007eb1',
    '#5BDCC7',
    '#97DC5C',
    '#FCD900',
    '#F89406',
    '#E82360',
    '#AA5580',
    '#6460AA',
    '#5793D4',
    '#1F74C0',
  ];
  return fullName
    ? colors[
        fullName
          .split('')
          .map((letter) => letter.charCodeAt(0))
          .reduce((sum, a) => sum + a, 0) % colors.length
      ]
    : colors[0];
};

const makeFormSchema = (intl) => ({
  fieldsets: [
    {
      id: 'default',
      fields: ['comment'],
    },
  ],
  properties: {
    comment: {
      title: intl.formatMessage(messages.comment),
      type: 'text',
      widget: 'textarea',
    },
  },
  required: ['comment'],
});

const messages = defineMessages({
  comment: {
    id: 'Comment',
    defaultMessage: 'Comment',
  },
  commentDescription: {
    id: 'You can add a comment by filling out the form below. Plain text formatting.',
    defaultMessage:
      'You can add a comment by filling out the form below. Plain text formatting.',
  },
  default: {
    id: 'Default',
    defaultMessage: 'Default',
  },
  reply: {
    id: 'Reply',
    defaultMessage: 'Reply',
  },
  edit: {
    id: 'Edit',
    defaultMessage: 'Edit',
  },
  delete: {
    id: 'Delete',
    defaultMessage: 'Delete',
  },
});

/**
 * Comments component class.
 * @function Comments
 * @param {Object} pathname Pathname of the object.
 * @returns {string} Markup of the component.
 */
const Comments = (props) => {
  const { pathname } = props;
  const dispatch = useDispatch();
  const [showEdit, setShowEdit] = useState(false);
  const [editId, setEditId] = useState(null);
  const [editText, setEditText] = useState(null);
  const [replyTo, setReplyTo] = useState(null);
  const [collapsedComments, setCollapsedComments] = useState({});

  const intl = useIntl();

  const comments = useSelector((state) => state.comments);
  const permissions = comments?.permissions || {};
  const items = comments?.items || [];
  const items_total = comments?.items_total || 0;

  const getColor = (username) =>
    getAvatarInternalColor((username || '').toUpperCase());

  useEffect(() => {
    setReplyTo(null);
  }, [comments.add.loaded]);

  const loadMoreComments = () => {
    dispatch(listMoreComments(pathname));
  };

  const onDelete = (value) => {
    dispatch(deleteComment(value));
  };

  const onEdit = (value) => {
    setEditId(value.id);
    setEditText(value.text);
    setShowEdit(true);
  };

  const onEditOk = (data) => {
    setShowEdit(false);
    setEditId(null);
    setEditText(null);
    dispatch(updateComment(editId, data.comment));
  };

  const onEditCancel = () => {
    setShowEdit(false);
    setEditId(null);
    setEditText(null);
    setReplyTo(null);
  };

  const onSubmit = (commentData) => {
    dispatch(addComment(pathname, commentData.comment, replyTo));
  };
  const hideReply = (comment_id) => {
    setCollapsedComments({
      ...collapsedComments,
      [comment_id]: !collapsedComments[comment_id],
    });
  };

  // adds comment-children to every comment-parent
  // every comment is represented with obj: {comment_id, children: [all the comments that have in_reply_to as the comment_id]}
  const addRepliesAsChildrenToComments = (items) => {
    const allCommentsWithCildren = {};
    // initializing all comment with children as empty array
    items.forEach((comment) => {
      allCommentsWithCildren[comment.comment_id] = {
        ...comment,
        children: [],
      };
    });
    // populating children arrays with comments (replies)
    items.forEach((comment) => {
      if (comment.in_reply_to) {
        if (allCommentsWithCildren[comment.in_reply_to]?.children) {
          allCommentsWithCildren[comment.in_reply_to].children.push(comment);
        }
      }
    });
    return allCommentsWithCildren;
  };

  const moment = props.moment.default;

  const allCommentsWithCildren = useMemo(
    () => addRepliesAsChildrenToComments(items),
    [items],
  );
  // all comments that are not a reply will be shown in the first iteration
  const allPrimaryComments = items.filter((comment) => !comment.in_reply_to);

  // recursively makes comments with their replies nested
  // each iteration will show replies to the specific comment using allCommentsWithCildren
  const commentElement = (comment) => (
    <Comment key={comment.comment_id}>
      <Avatar
        src={getPortraitUrl(comment.author_image)}
        title={comment.author_name || 'Anonymous'}
        color={getColor(comment.author_username)}
      />
      <Comment.Content>
        <Comment.Author>{comment.author_name}</Comment.Author>
        <Comment.Metadata>
          <span>
            {' '}
            <span title={moment(comment.creation_date).format('LLLL')}>
              {moment(comment.creation_date).fromNow()}
            </span>
          </span>
        </Comment.Metadata>
        <Comment.Text>
          {' '}
          {comment.text['mime-type'] === 'text/html' ? (
            <div
              dangerouslySetInnerHTML={{
                __html: comment.text.data,
              }}
            />
          ) : (
            comment.text.data
          )}
        </Comment.Text>
        <Comment.Actions>
          {comment.can_reply && (
            <Comment.Action
              as="a"
              aria-label={intl.formatMessage(messages.reply)}
              onClick={() => setReplyTo(comment.comment_id)}
            >
              <FormattedMessage id="Reply" defaultMessage="Reply" />
            </Comment.Action>
          )}
          {comment.is_editable && (
            <Comment.Action
              onClick={() =>
                onEdit({
                  id: flattenToAppURL(comment['@id']),
                  text: comment.text.data,
                })
              }
              aria-label={intl.formatMessage(messages.edit)}
              value={{
                id: flattenToAppURL(comment['@id']),
                text: comment.text.data,
              }}
            >
              <FormattedMessage id="Edit" defaultMessage="Edit" />
            </Comment.Action>
          )}
          {comment.is_deletable && (
            <Comment.Action
              aria-label={intl.formatMessage(messages.delete)}
              onClick={() => onDelete(flattenToAppURL(comment['@id']))}
              color="red"
            >
              <Icon name="delete" color="red" />
              <FormattedMessage
                id="Delete"
                defaultMessage="Delete"
                color="red"
              />
            </Comment.Action>
          )}
          <Comment.Action as="a" onClick={() => hideReply(comment.comment_id)}>
            {allCommentsWithCildren[comment.comment_id].children.length > 0 ? (
              collapsedComments[comment.comment_id] ? (
                <>
                  <Icon name="eye" color="blue" />
                  <FormattedMessage
                    id="Show Replies"
                    defaultMessage="Show Replies"
                  />
                </>
              ) : (
                <>
                  <Icon name="minus" color="blue" />
                  <FormattedMessage
                    id="Hide Replies"
                    defaultMessage="Hide Replies"
                  />
                </>
              )
            ) : null}
          </Comment.Action>
        </Comment.Actions>
        <div id={`reply-place-${comment.comment_id}`}></div>
      </Comment.Content>

      {allCommentsWithCildren[comment.comment_id].children.length > 0
        ? allCommentsWithCildren[comment.comment_id].children.map(
            (child, index) => (
              <Comment.Group
                collapsed={collapsedComments[comment.comment_id]}
                key={`group-${index}-${comment.comment_id}`}
              >
                {commentElement(child)}
              </Comment.Group>
            ),
          )
        : null}
    </Comment>
  );

  if (!permissions.view_comments) return '';

  return (
    <Container className="comments">
      <CommentEditModal
        open={showEdit}
        onCancel={onEditCancel}
        onOk={onEditOk}
        id={editId}
        text={editText}
      />
      {permissions.can_reply && (
        <div id="comment-add-id">
          <Form
            onSubmit={onSubmit}
            onCancel={onEditCancel}
            submitLabel={intl.formatMessage(messages.comment)}
            resetAfterSubmit
            schema={makeFormSchema(intl)}
          />
        </div>
      )}
      {/* all comments  */}
      <Comment.Group threaded>
        {allPrimaryComments.map((item) => commentElement(item))}
      </Comment.Group>

      {/* load more button */}
      {items_total > items.length && (
        <Button fluid basic color="blue" onClick={loadMoreComments}>
          <FormattedMessage id="Load more" defaultMessage="Load more..." />
        </Button>
      )}

      {replyTo && (
        <Portal
          node={document && document.getElementById(`reply-place-${replyTo}`)}
        >
          <Form
            onSubmit={onSubmit}
            onCancel={onEditCancel}
            submitLabel={intl.formatMessage(messages.comment)}
            resetAfterSubmit
            schema={makeFormSchema(intl)}
          />
        </Portal>
      )}
    </Container>
  );
};

Comments.propTypes = {
  pathname: PropTypes.string.isRequired,
};

export default compose(injectLazyLibs(['moment']))(Comments);